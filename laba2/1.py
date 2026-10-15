import streamlit as st

st.title("ИССЛЕДОВАНИЕ ВЛИЯНИЯ АЛГОРИТМА ГЕНЕРАЦИИ НА КАЧЕСТВО ВЫЧИСЛИТЕЛЬНОЙ СЕТКИ")
st.header("Влияние алгоритма генерации сетки на точность двумерной модельной задачи")
st.subheader("Постановка задачи")
st.write("Рассмотрим двумерную задачу об одноосном растяжении плоской неограниченной пластины с круговым вырезом.")
st.markdown(r"""
Геометрическая модель (размеры указаны в метрах):

- Ввиду симметрии задачи рассматривается 1/4 пластины
- $BC = 5\ \text{м}$
- Диаметр отверстия 0.5 м
- Используются полярные координаты

Граничные условия:

- Нулевые перемещения вдоль оси $X$ на прямой $AB$
- Нулевые перемещения вдоль оси $Y$ на прямой $ED$
- $P_0 = 1\ \text{МПа}$

Параметры материала:

- Изотропный
- Модуль упругости $E = 200\ \text{ГПа}$
- Коэффициент Пуассона $\nu = 0.3$
""")

st.markdown(r"""
Напряжение $\sigma_\theta$ в точке $E(0.25;\ 0;\ 0)$ равно **3 МПа с точностью 1%**.  
Значения вычислены по формуле:
""")

st.latex(r"\sigma_\theta^{max} = 3P_0")

st.markdown("Напишем уравнение изотропной упругости:")

st.latex(r"-\nabla \cdot \sigma = 0")
st.latex(r"\sigma = 2\mu\varepsilon_u + \lambda \operatorname{tr}(\varepsilon_u)I")
st.latex(r"\varepsilon_u = \frac{1}{2}\left(\nabla u + \nabla u^{T}\right)")

st.markdown(r"""
где $\lambda$ — постоянная Ламе, $\mu$ — модуль сдвига.  
Параметры Ламе:
""")

st.latex(r"\lambda = \frac{\nu E}{(1+\nu)(1-2\nu)}, \qquad \mu = \frac{E}{2(1+\nu)}")

st.text("Далее вывод слабой формы:")

st.latex(r"-(\nabla \cdot \sigma) \cdot v = 0")

st.latex(r"-\int_{\Omega} (\nabla \cdot \sigma) \cdot v \, dx = 0")

st.latex(r"\int_{\Omega} \sigma_u \varepsilon_v \, dx - \int_{\partial \Omega} v \cdot P_0 \, ds = 0")

st.divider()

code = '''from dolfin import *
meshname = "mesh-meshAdapt"
mesh = Mesh(meshname + ".xml")
subdomains = MeshFunction("size_t", mesh, meshname + "_physical_region.xml")
boundaries = MeshFunction("size_t", mesh, meshname + "_facet_region.xml")

E = 200e9
nu = 0.3
lmbda = (nu * E) / ((1 + nu)*(1 - 2*nu))
mu = E / (2*(1 + nu))
g = Constant(0.0)
P0 = Constant((0.0, 1.0e6))

def epsilon(u):
  return 0.5*(grad(u) + grad(u).T)

def sigma(u):
  return lmbda * div(u) * Identity(2) + 2*mu*epsilon(u)

V = VectorFunctionSpace(mesh, "CG", 1)

bc1 = DirichletBC(V.sub(0), g, boundaries, 1)
bc2 = DirichletBC(V.sub(1), g, boundaries, 2)
bcs = [bc1, bc2]

u = TrialFunction(V)
v = TestFunction(V)

dx = Measure('dx', domain=mesh, subdomain_data=subdomains)
ds = Measure('ds', domain=mesh, subdomain_data=boundaries)

a = inner(sigma(u), epsilon(v)) * dx
L = inner(P0, v) * ds(3)

u = Function(V)

solve(a == L, u, bcs)
File("./results/u.pvd") << u

W = TensorFunctionSpace(mesh, "CG", 1)
stress = project(sigma(u), V=W)
File("./results/s.pvd") << stress

point_E = Point(0.25, 0.0)
stress_values = stress(point_E)
sigma_yy = stress_values[3] / 1e6

print(f"Расчетное напряжение в точке E: {sigma_yy:.4f} МПа")
print("Ожидаемое теоретическое значение: 3.0 МПа")
print(f"Относительная погрешность: {abs((sigma_yy - 3)/3)*100}")
'''
st.code(code, language="python")