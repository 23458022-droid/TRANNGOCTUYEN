import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import colour

st.set_page_config(layout="wide")
st.write("## Biểu đồ CIELab và chuyển dịch màu Lab1 → Lab2")


def ma_hoa_srgb(v):
    v = np.clip(v, 0, 1)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - 0.055)


def lab_to_rgb(Lab):
    """Lab -> (XYZ, sRGB hiển thị, có nằm trong gamut sRGB không)."""
    XYZ = colour.Lab_to_XYZ(np.asarray(Lab, dtype=float))
    tuyen_tinh = colour.XYZ_to_sRGB(XYZ, apply_cctf_encoding=False)
    trong_gamut = bool(np.all((tuyen_tinh >= -1e-4) & (tuyen_tinh <= 1 + 1e-4)))
    return XYZ, ma_hoa_srgb(tuyen_tinh), trong_gamut


@st.cache_data
def nen_ab(L, lim=110, n=221):
    a, b = np.meshgrid(np.linspace(-lim, lim, n), np.linspace(lim, -lim, n))
    Lab = np.dstack((np.full_like(a, L), a, b))
    XYZ = colour.Lab_to_XYZ(Lab)
    tt = colour.XYZ_to_sRGB(XYZ, apply_cctf_encoding=False)
    ngoai = np.any(~np.isfinite(tt) | (tt < 0) | (tt > 1), axis=-1)
    rgb = ma_hoa_srgb(np.nan_to_num(tt))
    rgb[ngoai] = 0.92
    return rgb


def ten_mau(h, C):
    if C < 5:
        return "gần trung tính (xám)"
    ds = [(20, "đỏ"), (50, "cam"), (90, "vàng"), (150, "vàng lục"),
          (200, "lục"), (250, "lục lam (cyan)"), (300, "lam"),
          (340, "tím / magenta"), (360, "đỏ")]
    for gioi_han, ten in ds:
        if h < gioi_han:
            return ten
    return "đỏ"


# ------------------------------------------------------------ Nhập liệu
c1, c2 = st.columns(2)
with c1:
    st.write("### Màu Lab1")
    L1 = st.number_input("L1*", 0.0, 100.0, 50.0, key="L1")
    a1 = st.number_input("a1*", -128.0, 127.0, 40.0, key="a1")
    b1 = st.number_input("b1*", -128.0, 127.0, 30.0, key="b1")
with c2:
    st.write("### Màu Lab2")
    L2 = st.number_input("L2*", 0.0, 100.0, 65.0, key="L2")
    a2 = st.number_input("a2*", -128.0, 127.0, 20.0, key="a2")
    b2 = st.number_input("b2*", -128.0, 127.0, 60.0, key="b2")

Lab1 = np.array([L1, a1, b1])
Lab2 = np.array([L2, a2, b2])

XYZ1, rgb1, ok1 = lab_to_rgb(Lab1)
XYZ2, rgb2, ok2 = lab_to_rgb(Lab2)
xy1 = colour.XYZ_to_xy(XYZ1)
xy2 = colour.XYZ_to_xy(XYZ2)

# ------------------------------------------------------------ Tính toán
dL, da, db = Lab2 - Lab1
C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
h1 = np.degrees(np.arctan2(b1, a1)) % 360
h2 = np.degrees(np.arctan2(b2, a2)) % 360
dC = C2 - C1
dh = ((h2 - h1 + 180) % 360) - 180
dE76 = float(colour.delta_E(Lab1, Lab2, method="CIE 1976"))
dE00 = float(colour.delta_E(Lab1, Lab2, method="CIE 2000"))


def swatch(rgb, nhan):
    mau = "#%02X%02X%02X" % tuple((np.clip(rgb, 0, 1) * 255).round().astype(int))
    return (f"<div style='background:{mau};height:70px;border-radius:8px;"
            f"border:1px solid #888;'></div><p style='text-align:center'>{nhan}</p>")


s1, s2 = st.columns(2)
s1.markdown(swatch(rgb1, "Lab1"), unsafe_allow_html=True)
s2.markdown(swatch(rgb2, "Lab2"), unsafe_allow_html=True)
if not (ok1 and ok2):
    st.warning("Có màu nằm ngoài gamut sRGB, màu hiển thị chỉ là gần đúng.")

st.write("### Kết quả")
st.table({
    "Đại lượng": ["L*", "a*", "b*", "C*ab", "h°ab", "x", "y"],
    "Lab1": [f"{L1:.2f}", f"{a1:.2f}", f"{b1:.2f}", f"{C1:.2f}", f"{h1:.1f}",
             f"{xy1[0]:.4f}", f"{xy1[1]:.4f}"],
    "Lab2": [f"{L2:.2f}", f"{a2:.2f}", f"{b2:.2f}", f"{C2:.2f}", f"{h2:.1f}",
             f"{xy2[0]:.4f}", f"{xy2[1]:.4f}"],
    "Chênh lệch": [f"{dL:+.2f}", f"{da:+.2f}", f"{db:+.2f}", f"{dC:+.2f}",
                   f"{dh:+.1f}", f"{xy2[0]-xy1[0]:+.4f}", f"{xy2[1]-xy1[1]:+.4f}"],
})
m1, m2 = st.columns(2)
m1.metric("ΔE*ab (CIE 1976)", f"{dE76:.2f}")
m2.metric("ΔE00 (CIEDE2000)", f"{dE00:.2f}")

# ------------------------------------------------------------ Đồ thị
tab_ab, tab_xy, tab_3d = st.tabs(["Mặt phẳng a*b*", "Biểu đồ CIE xy", "Không gian 3D L*a*b*"])

with tab_ab:
    col, _ = st.columns([2, 1])
    with col:
        lim = 110
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(nen_ab((L1 + L2) / 2), extent=[-lim, lim, -lim, lim])
        for r in (25, 50, 75, 100):
            ax.add_patch(plt.Circle((0, 0), r, fill=False, ls="--", lw=0.6, color="gray"))
        ax.axhline(0, color="k", lw=0.8)
        ax.axvline(0, color="k", lw=0.8)
        ax.scatter([a1], [b1], s=160, c=[rgb1], edgecolors="k", zorder=3)
        ax.scatter([a2], [b2], s=160, c=[rgb2], edgecolors="k", zorder=3)
        ax.annotate("Lab1", (a1, b1), textcoords="offset points", xytext=(8, 8))
        ax.annotate("Lab2", (a2, b2), textcoords="offset points", xytext=(8, 8))
        ax.annotate("", xy=(a2, b2), xytext=(a1, b1),
                    arrowprops=dict(arrowstyle="->", lw=2, color="k"), zorder=2)
        ax.text(lim - 2, 4, "+a* (đỏ)", ha="right", fontsize=9)
        ax.text(-lim + 2, 4, "−a* (lục)", ha="left", fontsize=9)
        ax.text(4, lim - 8, "+b* (vàng)", fontsize=9)
        ax.text(4, -lim + 4, "−b* (lam)", fontsize=9)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_xlabel("a*")
        ax.set_ylabel("b*")
        ax.set_title(f"Mặt phẳng a*b* tại L* = {(L1 + L2) / 2:.0f}  (xám = ngoài gamut sRGB)")
        st.pyplot(fig, clear_figure=True)

with tab_xy:
    col, _ = st.columns([2, 1])
    with col:
        fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(show=False)
        ax.set_xlim(-0.1, 0.85)
        ax.set_ylim(-0.1, 0.90)
        ax.scatter([xy1[0]], [xy1[1]], s=90, c=[rgb1], edgecolors="k", zorder=5)
        ax.scatter([xy2[0]], [xy2[1]], s=90, c=[rgb2], edgecolors="k", zorder=5)
        ax.annotate("Lab1", xy1, textcoords="offset points", xytext=(8, 8), zorder=6)
        ax.annotate("Lab2", xy2, textcoords="offset points", xytext=(8, 8), zorder=6)
        ax.annotate("", xy=xy2, xytext=xy1,
                    arrowprops=dict(arrowstyle="->", lw=2, color="k"), zorder=4)
        ax.set_title("Chuyển dịch màu Lab1 → Lab2 trên biểu đồ CIE 1931")
        st.pyplot(fig, clear_figure=True)

with tab_3d:
    col, _ = st.columns([2, 1])
    with col:
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection="3d")
        ax.scatter([a1], [b1], [L1], s=120, c=[rgb1], edgecolors="k")
        ax.scatter([a2], [b2], [L2], s=120, c=[rgb2], edgecolors="k")
        ax.plot([a1, a2], [b1, b2], [L1, L2], "k-", lw=2)
        ax.text(a1, b1, L1, "Lab1")
        ax.text(a2, b2, L2, "Lab2")
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        ax.set_zlim(0, 100)
        ax.set_xlabel("a*")
        ax.set_ylabel("b*")
        ax.set_zlabel("L*")
        st.pyplot(fig, clear_figure=True)

# ------------------------------------------------------------ Nhận xét
st.write("### Nhận xét sự chuyển dịch màu")
nx = []
nx.append(f"- **Độ sáng:** ΔL* = {dL:+.2f} → " +
          ("màu 2 **sáng hơn** màu 1." if dL > 1 else
           "màu 2 **tối hơn** màu 1." if dL < -1 else "độ sáng gần như không đổi."))
nx.append(f"- **Trục đỏ–lục:** Δa* = {da:+.2f} → " +
          ("dịch về phía **đỏ** (bớt lục)." if da > 1 else
           "dịch về phía **lục** (bớt đỏ)." if da < -1 else "gần như không đổi."))
nx.append(f"- **Trục vàng–lam:** Δb* = {db:+.2f} → " +
          ("dịch về phía **vàng** (bớt lam)." if db > 1 else
           "dịch về phía **lam** (bớt vàng)." if db < -1 else "gần như không đổi."))
nx.append(f"- **Độ bão hoà:** ΔC* = {dC:+.2f} → " +
          ("màu 2 **sặc sỡ / bão hoà hơn**." if dC > 1 else
           "màu 2 **nhạt / xám hơn**." if dC < -1 else "độ bão hoà gần như không đổi."))
nx.append(f"- **Sắc độ (hue):** từ {h1:.0f}° ({ten_mau(h1, C1)}) sang {h2:.0f}° "
          f"({ten_mau(h2, C2)}), Δh = {dh:+.1f}°.")
if dE00 < 1:
    muc = "mắt thường gần như **không phân biệt** được."
elif dE00 < 2:
    muc = "chỉ phân biệt được khi quan sát kỹ."
elif dE00 < 3.5:
    muc = "phân biệt được nếu để ý."
elif dE00 < 5:
    muc = "khác biệt **khá rõ**."
else:
    muc = "hai màu **khác nhau rõ rệt**."
nx.append(f"- **Tổng thể:** ΔE00 = {dE00:.2f} (ΔE*ab = {dE76:.2f}) → {muc}")
st.markdown("\n".join(nx))
