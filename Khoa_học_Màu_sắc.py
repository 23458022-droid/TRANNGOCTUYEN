import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Khoa học Màu sắc", layout="wide")

THU_MUC_ANH = Path(__file__).parent / "images"


def hien_logo(ten_file, rong=150):
    duong_dan = THU_MUC_ANH / ten_file
    if duong_dan.exists():
        st.image(str(duong_dan), width=rong)
    else:
        st.caption(f"(Chưa có file images/{ten_file})")


col_trai, col_giua, col_phai = st.columns([1, 3, 1])
with col_trai:
    hien_logo("logo_truong.png")
with col_phai:
    hien_logo("logo_khoa.png")
with col_giua:
    st.markdown(
        "<h2 style='text-align:center;'>Chào mừng bạn đến với project Khoa học Màu sắc của mình!</h2>"
        "<h1 style='text-align:center;'>Mình tên là Võ Tự Thanh, MaSV 22158139</h1>",
        unsafe_allow_html=True,
    )

st.divider()
st.markdown(
    """
### Nội dung của trang web
1. Chuyển đổi không gian màu sRGB ⇄ XYZ
2. Tính giá trị 3 thành phần X, Y, Z từ file phổ
3. Biểu đồ CIE hình móng ngựa
4. Gamut màu của thiết bị RGB
5. Gamut màu của máy in (từ file gamut)
6. Đặc tính hoá máy in nửa tông
7. **Biểu đồ CIE dạng band (400 – 700 nm)**
8. **Biểu đồ CIELab và nhận xét chuyển dịch màu Lab1 → Lab2**
9. **So sánh gamut các không gian màu và máy in**

👈 Chọn trang ở thanh bên trái.
"""
)
