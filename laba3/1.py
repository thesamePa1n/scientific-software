from datetime import date, time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Оплата коммунальных услуг", layout="wide",)
st.title("Оплата коммунальных услуг")

color_col, period_col = st.columns([1, 2])
with color_col:
    receipt_color = st.color_picker("Цвет квитанции", "#1565C0")
with period_col:
    period = st.selectbox(
        "Расчётный период",
        ["Октябрь 2026", "Сентябрь 2026", "Август 2026", "Июль 2026", "Июнь 2026"],
    )

st.subheader("1. Данные плательщика")
left, right = st.columns(2)
with left:
    payer = st.text_input("ФИО плательщика", placeholder="Иванов Иван Иванович")
    account_number = st.text_input("Лицевой счёт", placeholder="Например, 123456789")
with right:
    address = st.text_input("Адрес помещения", placeholder="Город, улица, дом, квартира")
    recipient = st.pills(
        "Получатель платежа",
        ["УК / ТСЖ", "Ресурсоснабжающая организация", "Региональный оператор"],
        selection_mode="single",
        default="УК / ТСЖ",
    )

st.subheader("2. Выберите услуги")
services = st.multiselect(
    "Коммунальные услуги для расчёта",
    ["Холодная вода", "Горячая вода", "Электроэнергия", "Газ"],
    default=["Холодная вода", "Горячая вода", "Электроэнергия", "Газ"],
    help="Можно выбрать одну или несколько услуг.",
)

method = st.segmented_control(
    "Предпочтительный способ оплаты после расчёта",
    ["Банковская карта", "СБП", "Через банк"],
    default="Банковская карта",
    selection_mode="single",
)

electric_mode = st.radio(
    "Тариф электроэнергии",
    ["Однотарифный", "День / ночь"],
    horizontal=True,
    help="Для двухтарифного счётчика укажите дневные и ночные показания отдельно.",
)

with st.expander("Настроить тарифы", expanded=False):
    tariff1, tariff2, tariff3, tariff4 = st.columns(4)
    with tariff1:
        cold_tariff = st.number_input("Холодная вода, ₽/м³", min_value=0.0, value=45.0, step=1.0, key="cold_tariff")
    with tariff2:
        hot_tariff = st.number_input("Горячая вода, ₽/м³", min_value=0.0, value=220.0, step=1.0, key="hot_tariff")
    with tariff3:
        electricity_day_tariff = st.number_input("Электроэнергия день, ₽/кВт·ч", min_value=0.0, value=6.5, step=0.1, key="electricity_day_tariff")
    with tariff4:
        electricity_night_tariff = st.number_input("Электроэнергия ночь, ₽/кВт·ч", min_value=0.0, value=3.0, step=0.1, key="electricity_night_tariff")
    tariff5, tariff6 = st.columns(2)
    with tariff5:
        electricity_single_tariff = st.number_input("Однотарифная электроэнергия, ₽/кВт·ч", min_value=0.0, value=6.0, step=0.1, key="electricity_single_tariff")
    with tariff6:
        gas_tariff = st.number_input("Газ, ₽/м³", min_value=0.0, value=8.5, step=0.1, key="gas_tariff")

st.subheader("3. Показания счётчиков")
read_source = st.pills(
    "Как были получены показания?",
    ["Сняты самостоятельно", "Переданы УК", "Оценочные"],
    selection_mode="single",
    default="Сняты самостоятельно",
)

include_debt = st.toggle("Добавить задолженность за прошлый период", value=False)
debt_amount = 0.0
if include_debt:
    debt_amount = st.number_input("Сумма задолженности, ₽", min_value=0.0, value=0.0, step=100.0)

advance_payment = st.slider(
    "Дополнительный платёж в счёт будущих начислений, ₽",
    min_value=0,
    max_value=2000,
    value=0,
    step=100,
)

meter_photo = st.file_uploader(
    "Прикрепить фото счётчика (необязательно)",
    type=["png", "jpg", "jpeg"],
)
if meter_photo is not None:
    st.image(meter_photo, caption=f"Загружено: {meter_photo.name}", width=320)

with st.form("utility_payment_form"):
    st.markdown("#### Введите предыдущие и текущие показания")
    st.caption("Текущие показания должны быть не меньше предыдущих. Если услуга не выбрана, её показания не участвуют в расчёте.")

    readings = {}
    if "Холодная вода" in services:
        st.markdown("**Холодная вода (м³)**")
        c1, c2 = st.columns(2)
        with c1:
            readings["cold_previous"] = st.number_input("Предыдущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="cold_previous")
        with c2:
            readings["cold_current"] = st.number_input("Текущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="cold_current")

    if "Горячая вода" in services:
        st.markdown("**Горячая вода (м³)**")
        c1, c2 = st.columns(2)
        with c1:
            readings["hot_previous"] = st.number_input("Предыдущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="hot_previous")
        with c2:
            readings["hot_current"] = st.number_input("Текущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="hot_current")

    if "Электроэнергия" in services:
        st.markdown("**Электроэнергия**")
        if electric_mode == "Однотарифный":
            c1, c2 = st.columns(2)
            with c1:
                readings["electric_previous"] = st.number_input("Предыдущие показания, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_previous")
            with c2:
                readings["electric_current"] = st.number_input("Текущие показания, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_current")
        else:
            st.markdown("Дневной тариф")
            c1, c2 = st.columns(2)
            with c1:
                readings["electric_day_previous"] = st.number_input("Предыдущие дневные, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_day_previous")
            with c2:
                readings["electric_day_current"] = st.number_input("Текущие дневные, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_day_current")
            st.markdown("Ночной тариф")
            c1, c2 = st.columns(2)
            with c1:
                readings["electric_night_previous"] = st.number_input("Предыдущие ночные, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_night_previous")
            with c2:
                readings["electric_night_current"] = st.number_input("Текущие ночные, кВт·ч", min_value=0.0, value=0.0, step=1.0, key="electric_night_current")

    if "Газ" in services:
        st.markdown("**Газ (м³)**")
        c1, c2 = st.columns(2)
        with c1:
            readings["gas_previous"] = st.number_input("Предыдущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="gas_previous")
        with c2:
            readings["gas_current"] = st.number_input("Текущие показания", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="gas_current")

    st.markdown("#### Дата передачи показаний")
    d_col, t_col = st.columns(2)
    with d_col:
        reading_date = st.date_input("Дата", value=date.today(), format="DD/MM/YYYY")
    with t_col:
        reading_time = st.time_input("Время", value=time(12, 0), step=900)

    confirmed = st.checkbox("Подтверждаю, что ввёл показания без ошибок")
    submitted = st.form_submit_button("Рассчитать начисления", type="primary", use_container_width=True)

if submitted:
    errors = []
    if not payer.strip():
        errors.append("Введите ФИО плательщика.")
    if not account_number.strip():
        errors.append("Введите номер лицевого счёта.")
    if not address.strip():
        errors.append("Введите адрес помещения.")
    if not services:
        errors.append("Выберите хотя бы одну коммунальную услугу.")
    if not confirmed:
        errors.append("Подтвердите правильность введённых показаний.")

    pairs_to_check = []
    if "Холодная вода" in services:
        pairs_to_check.append(("cold_previous", "cold_current", "Холодная вода"))
    if "Горячая вода" in services:
        pairs_to_check.append(("hot_previous", "hot_current", "Горячая вода"))
    if "Электроэнергия" in services:
        if electric_mode == "Однотарифный":
            pairs_to_check.append(("electric_previous", "electric_current", "Электроэнергия"))
        else:
            pairs_to_check.append(("electric_day_previous", "electric_day_current", "Электроэнергия (день)"))
            pairs_to_check.append(("electric_night_previous", "electric_night_current", "Электроэнергия (ночь)"))
    if "Газ" in services:
        pairs_to_check.append(("gas_previous", "gas_current", "Газ"))

    for previous_key, current_key, service_name in pairs_to_check:
        if readings[current_key] < readings[previous_key]:
            errors.append(f"Для услуги «{service_name}» текущие показания меньше предыдущих.")

    if errors:
        st.session_state.pop("utility_receipt", None)
        for error in errors:
            st.error(error)
    else:
        rows = []

        def add_row(service, previous, current, unit, tariff, amount):
            rows.append({
                "Услуга": service,
                "Предыдущие показания": previous,
                "Текущие показания": current,
                "Расход": round(current - previous, 3),
                "Единица": unit,
                "Тариф, ₽": round(tariff, 2),
                "Начислено, ₽": round(amount, 2),
            })

        if "Холодная вода" in services:
            consumption = readings["cold_current"] - readings["cold_previous"]
            add_row("Холодная вода", readings["cold_previous"], readings["cold_current"], "м³", cold_tariff, consumption * cold_tariff)

        if "Горячая вода" in services:
            consumption = readings["hot_current"] - readings["hot_previous"]
            add_row("Горячая вода", readings["hot_previous"], readings["hot_current"], "м³", hot_tariff, consumption * hot_tariff)

        if "Электроэнергия" in services:
            if electric_mode == "Однотарифный":
                consumption = readings["electric_current"] - readings["electric_previous"]
                add_row("Электроэнергия", readings["electric_previous"], readings["electric_current"], "кВт·ч", electricity_single_tariff, consumption * electricity_single_tariff)
            else:
                day_consumption = readings["electric_day_current"] - readings["electric_day_previous"]
                night_consumption = readings["electric_night_current"] - readings["electric_night_previous"]
                total_consumption = day_consumption + night_consumption
                total_amount = day_consumption * electricity_day_tariff + night_consumption * electricity_night_tariff
                rows.append({
                    "Услуга": "Электроэнергия (день / ночь)",
                    "Предыдущие показания": f"{readings['electric_day_previous']} / {readings['electric_night_previous']}",
                    "Текущие показания": f"{readings['electric_day_current']} / {readings['electric_night_current']}",
                    "Расход": round(total_consumption, 3),
                    "Единица": "кВт·ч",
                    "Тариф, ₽": f"день {electricity_day_tariff:.2f}; ночь {electricity_night_tariff:.2f}",
                    "Начислено, ₽": round(total_amount, 2),
                })

        if "Газ" in services:
            consumption = readings["gas_current"] - readings["gas_previous"]
            add_row("Газ", readings["gas_previous"], readings["gas_current"], "м³", gas_tariff, consumption * gas_tariff)

        details = pd.DataFrame(rows)
        services_total = float(details["Начислено, ₽"].sum())
        final_total = services_total + float(debt_amount) + float(advance_payment)
        receipt = {
            "payer": payer.strip(),
            "account_number": account_number.strip(),
            "address": address.strip(),
            "recipient": recipient,
            "period": period,
            "payment_method": method,
            "reading_source": read_source,
            "reading_date": reading_date.strftime("%d.%m.%Y"),
            "reading_time": reading_time.strftime("%H:%M"),
            "services": services,
            "details": details,
            "services_total": round(services_total, 2),
            "debt_amount": round(float(debt_amount), 2),
            "advance_payment": round(float(advance_payment), 2),
            "final_total": round(final_total, 2),
            "receipt_color": receipt_color,
        }
        st.session_state["utility_receipt"] = receipt


receipt = st.session_state.get("utility_receipt")
if receipt:
    st.divider()
    st.markdown(
        f"<div style='background:{receipt['receipt_color']}; padding:16px; border-radius:10px; color:white;'>"
        f"<h2 style='margin:0; color:white;'>Квитанция за {receipt['period']}</h2>"
        f"<div>Лицевой счёт: {receipt['account_number']}</div></div>",
        unsafe_allow_html=True,
    )
    st.write(f"**Плательщик:** {receipt['payer']}")
    st.write(f"**Адрес:** {receipt['address']}")
    st.write(f"**Получатель:** {receipt['recipient']}")
    st.write(f"**Дата и время передачи показаний:** {receipt['reading_date']} {receipt['reading_time']}")

    st.subheader("Расчёт начислений")
    st.dataframe(receipt["details"], use_container_width=True, hide_index=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Начисления за услуги", f"{receipt['services_total']:.2f} ₽")
    m2.metric("Задолженность", f"{receipt['debt_amount']:.2f} ₽")
    m3.metric("Аванс", f"{receipt['advance_payment']:.2f} ₽")
    m4.metric("Итого к оплате", f"{receipt['final_total']:.2f} ₽")