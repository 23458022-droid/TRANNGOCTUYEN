import streamlit as st
import numpy as np
import pandas as pd
import colour

st.set_page_config(layout="wide")
st.write("## So sánh gamut các không gian màu và máy in")

KHONG_GIAN = ["sRGB", "Display P3", "Adobe RGB (1998)", "ITU-R BT.2020"]
MAU_VE = {"sRGB": "k", "Display P3": "tab:blue",
          "Adobe RGB (1998)": "tab:green", "ITU-R BT.2020": "tab:red"}


def dien_tich(tam_giac):
    """Diện tích đa giác trong mặt phẳng xy (công thức Shoelace)."""
    x, y = tam_giac[:, 0], tam_giac[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


chon = st.sidebar.multiselect("Chọn không gian màu", KHONG_GIAN, default=["sRGB", "Adobe RGB (1998)"])
csv_file = st.sidebar.file_uploader("(Tuỳ chọn) File gamut máy in .csv", type=["csv"])

fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(show=False)
ax.set_xlim(-0.1, 0.85)
ax.set_ylim(-0.1, 0.90)
ax.set_title("So sánh gamut trên biểu đồ CIE 1931")

ket_qua = []
dien_tich_srgb = dien_tich(np.asarray(colour.RGB_COLOURSPACES["sRGB"].primaries))

for ten in chon:
    prim = np.asarray(colour.RGB_COLOURSPACES[ten].primaries)
    ax.plot(*np.vstack([prim, prim[:1]]).T, color=MAU_VE[ten], lw=2, label=ten)
    S = dien_tich(prim)
    ket_qua.append({"Thiết bị / không gian": ten, "Diện tích (xy)": round(S, 4),
                    "So với sRGB (%)": round(100 * S / dien_tich_srgb, 1)})

if csv_file is not None:
    df = pd.read_csv(csv_file).set_index("ColorSpace")
    # Thứ tự các đỉnh giống trang 5: R, Y, G, C, B, M
    pts = []
    for cot in ["R", "Y", "G", "C", "B", "M"]:
        Lab = df[cot].to_numpy(dtype=float)
        pts.append(colour.XYZ_to_xy(colour.Lab_to_XYZ(Lab)))
    pts = np.array(pts)
    ax.plot(*np.vstack([pts, pts[:1]]).T, color="tab:orange", lw=2, label="Máy in (file)")
    S = dien_tich(pts)
    ket_qua.append({"Thiết bị / không gian": "Máy in (file)", "Diện tích (xy)": round(S, 4),
                    "So với sRGB (%)": round(100 * S / dien_tich_srgb, 1)})

if chon or csv_file is not None:
    ax.legend(loc="upper right")

col1, col2 = st.columns([2, 1])
with col1:
    st.pyplot(fig, clear_figure=True)
with col2:
    if ket_qua:
        st.write("### Diện tích gamut")
        st.dataframe(pd.DataFrame(ket_qua), hide_index=True)
        st.caption("Diện tích tính trên mặt phẳng xy; chỉ mang tính so sánh tương đối.")
    else:
        st.info("Hãy chọn ít nhất một không gian màu ở thanh bên.")
