import streamlit as st
import pandas as pd
import numpy as np

st.write("Привет, Streamlit! :sunglasses:")
st.write(pd.DataFrame(np.random.randint(1, 100, size=(3, 2))))