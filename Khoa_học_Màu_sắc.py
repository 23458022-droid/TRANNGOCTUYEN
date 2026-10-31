import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Khoa học Màu sắc", layout="wide")

# Thư mục chứa file này (không phụ thuộc vào nơi chạy lệnh streamlit)
THU_MUC_GOC = Path(__file__).resolve().parent
NOI_TIM_LOGO = [THU_MUC_GOC / "images", THU_MUC_GOC]
DUOI_ANH = [".png", ".jpg", ".jpeg", ".webp"]


def tim_logo(ten_goc):
    """Tìm logo theo tên (không cần đúng đuôi file, không phân biệt hoa/thường)."""
    for thu_muc in NOI_TIM_LOGO:
        if not thu_muc.exists():
            continue
        for f in thu_muc.iterdir():
            if f.stem.lower() == ten_goc.lower() and f.suffix.lower() in DUOI_ANH:
                return f
    return None


def hien_logo(ten_goc, rong=170):
    f = tim_logo(ten_goc)
    if f is None:
        st.warning(f"Không tìm thấy '{ten_goc}.png'. Hãy đặt file vào: {THU_MUC_GOC / 'images'}")
        return
    # Đọc file thành bytes để tránh lỗi đường dẫn có dấu tiếng Việt
    st.image(f.read_bytes(), width=rong)


# ------------------------------------------------------------ Đầu trang
col_trai, col_giua, col_phai = st.columns([1, 4, 1], vertical_alignment="center")
with col_trai:
    hien_logo("logo_truong")
with col_giua:
    st.markdown(
        """
<div style='text-align:center;'>
  <h3 style='margin-bottom:0;'>TRƯỜNG ĐẠI HỌC CÔNG NGHỆ KỸ THUẬT TP. HỒ CHÍ MINH</h3>
  <h4 style='margin-top:4px;'>KHOA IN VÀ TRUYỀN THÔNG</h4>
  <h1>Khoa học Màu sắc</h1>
  <h4>Chào mừng bạn đến với project Khoa học Màu sắc của mình!</h4>
  <h3>Mình tên là Trần Ngọc Tuyền, MSSV 23458022</h3>
</div>
""",
        unsafe_allow_html=True,
    )
with col_phai:
    hien_logo("logo_khoa")

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
