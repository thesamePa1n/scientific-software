import streamlit as st
import time
import random

def generate_random_numbers():
    for _ in range(10):
        number = random.randint(1, 50)
        yield f"{number} "
        time.sleep(0.5)
        
st.write_stream(generate_random_numbers())