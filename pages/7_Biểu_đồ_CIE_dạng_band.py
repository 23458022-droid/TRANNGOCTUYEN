import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import colour

st.set_page_config(layout="wide")
st.write("## Biểu đồ CIE dạng band (400 – 700 nm)")

WL_MIN, WL_MAX = 400, 700
cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]


def ma_hoa_srgb(rgb_tuyen_tinh):
    """Mã hoá gamma sRGB cho giá trị tuyến tính trong [0, 1]."""
    return np.where(
        rgb_tuyen_tinh <= 0.0031308,
        12.92 * rgb_tuyen_tinh,
        1.055 * np.power(rgb_tuyen_tinh, 1 / 2.4) - 0.055,
    )


@st.cache_data
def tinh_pho_mau(wl_min, wl_max):
    wl = np.asarray(cmfs.wavelengths, dtype=float)
    mask = (wl >= wl_min) & (wl <= wl_max)
    wl = wl[mask]
    XYZ = np.asarray(cmfs.values, dtype=float)[mask]
    xy = XYZ[:, :2] / XYZ.sum(axis=1, keepdims=True)

    # XYZ -> sRGB tuyến tính, cắt phần âm (ngoài gamut), chuẩn hoá về max = 1
    rgb = colour.XYZ_to_sRGB(XYZ, apply_cctf_encoding=False)
    rgb = np.clip(rgb, 0, None)
    rgb = rgb / rgb.max(axis=1, keepdims=True)
    rgb = np.clip(ma_hoa_srgb(rgb), 0, 1)
    return wl, XYZ, xy, rgb


wl, XYZ, xy, rgb = tinh_pho_mau(WL_MIN, WL_MAX)

buoc_nhan = st.sidebar.select_slider(
    "Bước nhãn bước sóng (nm)", options=[10, 20, 25, 50], value=20
)

tab1, tab2, tab3 = st.tabs(
    ["Band quang phổ", "Spectral locus dạng band", "Hàm màu CIE 1931"]
)

# ---------------------------------------------------------------- Tab 1
with tab1:
    img = np.tile(rgb[np.newaxis, :, :], (80, 1, 1))
    fig, ax = plt.subplots(figsize=(10, 2.8))
    ax.imshow(img, extent=[wl[0], wl[-1], 0, 1], aspect="auto")
    ax.set_yticks([])
    ax.set_xticks(np.arange(WL_MIN, WL_MAX + 1, 50))
    ax.set_xlabel("Bước sóng (nm)")
    ax.set_title("Dải màu quang phổ nhìn thấy (400 – 700 nm)")
    st.pyplot(fig, clear_figure=True)

# ---------------------------------------------------------------- Tab 2
with tab2:
    col, _ = st.columns([2, 1])
    with col:
        diem = xy.reshape(-1, 1, 2)
        doan = np.concatenate([diem[:-1], diem[1:]], axis=1)
        lc = LineCollection(doan, colors=rgb[:-1], linewidths=10, capstyle="round")

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.add_collection(lc)
        # đường nối hai đầu mút (đường tím)
        ax.plot([xy[0, 0], xy[-1, 0]], [xy[0, 1], xy[-1, 1]], "--", color="gray", lw=1.5)

        tam = np.array([0.33, 0.33])
        for i, w in enumerate(wl):
            if int(w) % buoc_nhan == 0:
                huong = xy[i] - tam
                huong = huong / np.linalg.norm(huong)
                p_nhan = xy[i] + 0.045 * huong
                ax.plot(
                    [xy[i, 0], xy[i, 0] + 0.02 * huong[0]],
                    [xy[i, 1], xy[i, 1] + 0.02 * huong[1]],
                    "k", lw=1,
                )
                ax.text(p_nhan[0], p_nhan[1], f"{int(w)}", ha="center", va="center", fontsize=8)

        ax.set_xlim(-0.1, 0.85)
        ax.set_ylim(-0.1, 0.90)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_title("Spectral locus 400 – 700 nm (CIE 1931 2°)")
        st.pyplot(fig, clear_figure=True)

# ---------------------------------------------------------------- Tab 3
with tab3:
    col, _ = st.columns([2, 1])
    with col:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(wl, XYZ[:, 0], "r", label="x̄(λ)")
        ax.plot(wl, XYZ[:, 1], "g", label="ȳ(λ)")
        ax.plot(wl, XYZ[:, 2], "b", label="z̄(λ)")
        ax.set_xlim(WL_MIN, WL_MAX)
        ax.set_xlabel("Bước sóng (nm)")
        ax.set_ylabel("Giá trị hàm màu")
        ax.set_title("Hàm phối màu CIE 1931 2° Standard Observer")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig, clear_figure=True)

st.info(
    "Màu hiển thị là màu sRGB gần đúng: các bước sóng nằm ngoài gamut sRGB "
    "được cắt về biên gamut và chuẩn hoá độ sáng."
)
