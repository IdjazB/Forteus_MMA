import streamlit as st

st.set_page_config(
    # Set page configuration
    page_title="MMA", layout="wide")

with st.sidebar:
    image = "https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png"  # Replace with the actual path to your photo
    image_size = (300, 200)  # Replace with the desired width and height of the image in pixels
        #st.image(image, width=image_size[0], use_column_width=False)
    st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="{image}" width="{image_size[0]}"></div>',
            unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: center;"><h1>July Market Update</h1></div>', unsafe_allow_html=True)
        #st.markdown("# July Market Update")