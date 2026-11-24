import sys
import os
import subprocess
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
# TỰ ĐỘNG CHẠY KHI NHẤN RUN HOẶC F5 TRONG PYTHON 
if not st.runtime.exists():
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
    sys.exit()

def doc_file_chuong_toan_dien(filepath):
  if not os.path.exists(filepath):
    return [], [], []

  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  part3_text, part2_text, part1_text = "", "", ""

  # Tách Phần 3
  if "[PHẦN 3: CÂU HỎI TRẢ LỜI NGẮN]" in content:
    split_p3 = content.split("[PHẦN 3: CÂU HỎI TRẢ LỜI NGẮN]")
    part3_text = split_p3[1].strip()
    rem = split_p3[0]
  else:
    rem = content

  # Tách Phần 2 và Phần 1
  if "[PHẦN 2: TRẮC NGHIỆM ĐÚNG SAI]" in rem:
    split_p2 = rem.split("[PHẦN 2: TRẮC NGHIỆM ĐÚNG SAI]")
    part2_text = split_p2[1].strip()
    part1_text = split_p2[0].replace(
        "[PHẦN 1: TRẮC NGHIỆM NHIỀU LỰA CHỌN]", ""
    ).strip()
  else:
    part1_text = rem.replace(
        "[PHẦN 1: TRẮC NGHIỆM NHIỀU LỰA CHỌN]", ""
    ).strip()

  # 1. Trích xuất Phần 1: Trắc nghiệm 4 lựa chọn
  ds_mcq = []
  blocks1 = [b.strip() for b in part1_text.split("---") if b.strip()]
  for b in blocks1:
    lines = [l.strip() for l in b.split("\n") if l.strip()]
    q_text, opts, ans, exp = "", [], "", ""
    for l in lines:
      if l.startswith("Câu "):
        q_text = l.split(":", 1)[1].strip() if ":" in l else l
      elif any(l.startswith(p) for p in ["A.", "B.", "C.", "D."]):
        opts.append(l)
      elif l.startswith("Đáp án:"):
        ans = l.replace("Đáp án:", "").strip()
      elif l.startswith("Giải thích:"):
        exp = l.replace("Giải thích:", "").strip()
    if q_text and len(opts) == 4 and ans:
      ds_mcq.append({
          "cau_hoi": q_text,
          "lua_chon": opts,
          "dap_an": ans,
          "giai_thich": exp,
      })

  # 2. Trích xuất Phần 2: Trắc nghiệm Đúng / Sai
  ds_tf = []
  blocks2 = [b.strip() for b in part2_text.split("---") if b.strip()]
  for b in blocks2:
    lines = [l.strip() for l in b.split("\n") if l.strip()]
    title, context = "", ""
    sub_items, curr_item = [], {}
    for l in lines:
      if l.startswith("Câu "):
        title = l.split(":", 1)[1].strip() if ":" in l else l
      elif l.startswith("Thông tin:"):
        context = l.replace("Thông tin:", "").strip()
      elif any(l.startswith(f"{c})") for c in ["a", "b", "c", "d"]):
        if curr_item:
          sub_items.append(curr_item)
        curr_item = {
            "label": l[:2],
            "statement": l[2:].strip(),
            "ans": "",
            "exp": "",
        }
      elif any(
          l.startswith(f"Đáp án {c}:") for c in ["a", "b", "c", "d"]
      ) and curr_item:
        curr_item["ans"] = l.split(":", 1)[1].strip()
      elif any(
          l.startswith(f"Giải thích {c}:") for c in ["a", "b", "c", "d"]
      ) and curr_item:
        curr_item["exp"] = l.split(":", 1)[1].strip()
    if curr_item:
      sub_items.append(curr_item)
    if title and len(sub_items) == 4:
      ds_tf.append({"tieu_de": title, "thong_tin": context, "y": sub_items})

  # 3. Trích xuất Phần 3: Trắc nghiệm Trả lời ngắn
  ds_sa = []
  blocks3 = [b.strip() for b in part3_text.split("---") if b.strip()]
  for b in blocks3:
    lines = [l.strip() for l in b.split("\n") if l.strip()]
    q_text, ans, exp = "", "", ""
    for l in lines:
      if l.startswith("Câu "):
        q_text = l.split(":", 1)[1].strip() if ":" in l else l
      elif l.startswith("Đáp án:"):
        ans = l.replace("Đáp án:", "").strip()
      elif l.startswith("Giải thích:"):
        exp = l.replace("Giải thích:", "").strip()
    if q_text and ans:
      ds_sa.append({"cau_hoi": q_text, "dap_an": ans, "giai_thich": exp})

  return ds_mcq, ds_tf, ds_sa


# CẤU HÌNH GIAO DIỆN HỆ THỐNG 
st.set_page_config(
    page_title="Phòng thí nghiệm - Số Hóa Tương Tác Địa lý 10",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

#  THANH ĐIỀU HƯỚNG BÊN TRÁI 
st.sidebar.title("📚 ĐỊA LÍ 10 ")
st.sidebar.caption("Hệ thống phần mềm học tập & mô phỏng khoa học kĩ thuật")

menu = st.sidebar.radio(
    "CHỌN MÔ-ĐUN HỌC TẬP & TƯƠNG TÁC:",
    [
        "1. Trang chủ & Giới thiệu chương trình",
        "2. Khí quyển: Mô phỏng Hiệu ứng Phơn (Bài 9)",
        "3. Thực hành: Phân tích biểu đồ khí hậu & Chẩn đoán AI (Bài 10)",
        "4. Thủy quyển: Phân tích thủy chế Sông Hồng (Bài 13)",
        "5. Sinh quyển & Vỏ địa lí: Quy luật đai cao (Bài 15, 18)",
        "6. Tra cứu thuật ngữ & Luyện tập tương tác",
        "7. 🎮 Trạm trò chơi thư giãn & Giảm stress ",
        "8. ôn tập, kiểm tra"
    ]
)

#  MÔ-ĐUN 1: TRANG CHỦ & TỔNG QUAN 
if menu == "1. Trang chủ & Giới thiệu chương trình":
    st.header("🌍 HỆ SINH THÁI THỰC HÀNH ĐỊA LÍ 10 TƯƠNG TÁC ")
    st.markdown("""
    Hệ thống phần mềm số hóa và chuyển đổi số toàn bộ nội dung **Sách giáo khoa Địa lí 10**,
    tích hợp mô hình hóa dữ liệu, hệ thống tính toán động học, cây quyết định trí tuệ chuyên gia và trạm mini-game giải trí giảm tải áp lực học tập 
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("🗺️ **Bản đồ số & WebGIS**nnTrực quan hóa hoàn lưu khí quyển, đới khí hậu, phương pháp biểu hiện không gian ")
    with col2:
        st.success("🔬 **Mô phỏng Động học**nnTương tác thời gian thực với hiệu ứng Phơn, quy luật đoạn nhiệt, vành đai thực vật ")
    with col3:
        st.warning("📊 **Trạm phân tích tự động**nnXử lý biểu đồ khí hậu, thủy chế sông ngòi và cây quyết định chẩn đoán tự động ")
    with col4:
        st.error("🎮 **GeoArcade Thư giãn**nnCác trò chơi trí tuệ ngắn giúp giải tỏa căng thẳng sau các bài tính toán số liệu.")

#  MÔ-ĐUN 2: HIỆU ỨNG PHƠN (BÀI 9) 
elif menu == "2. Khí quyển: Mô phỏng Hiệu ứng Phơn (Bài 9)":
    st.header("⛰️ Mô Phỏng Động Học: Quy Luật Biến Tính Đoạn Nhiệt & Gió Phơn")
    st.caption("Bám sát kiến thức Bài 9 - Chương 4: Khí quyển và bài tập thực tế dãy Trường Sơn")

    col_ctrl, col_graph = st.columns([1, 2])

    with col_ctrl:
        st.subheader("Tham số biến thiên")
        altitude = st.slider("Độ cao đỉnh núi (m):", min_value=500, max_value=3000, value=1500, step=100)
        t_base = st.slider("Nhiệt độ chân núi sườn đón gió (°C):", min_value=20.0, max_value=35.0, value=28.0, step=0.5)
        humidity_base = st.slider("Độ ẩm ban đầu chân núi Tây (%):", min_value=70, max_value=100, value=88)

        # Công thức đoạn nhiệt khí tượng bám sát SGK
        t_summit = t_base - 0.6 * (altitude / 100)
        t_leeward = t_summit + 1.0 * (altitude / 100)
        humidity_leeward = max(25, int(humidity_base - (altitude / 100) * 3.2))

        st.markdown("---")
        st.markdown("**Kết quả tại chân sườn khuất gió (Đông Trường Sơn):**")
        st.metric(label="Nhiệt độ chân núi sườn Đông", value=f"{t_leeward:.1f} °C", delta=f"+{t_leeward - t_base:.1f} °C (Khô nóng)")
        st.metric(label="Độ ẩm sườn Đông", value=f"{humidity_leeward} %", delta=f"-{humidity_base - humidity_leeward} %", delta_color="inverse")

    with col_graph:
        x_pts = [0, 50, 100]
        alt_pts = [0, altitude, 0]
        temp_pts = [t_base, t_summit, t_leeward]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(go.Scatter(
            x=x_pts, y=alt_pts, name="Địa hình núi", fill='tozeroy',
            line=dict(color='forestgreen', width=3), mode='lines'
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=x_pts, y=temp_pts, name="Tiến trình Nhiệt độ (°C)",
            line=dict(color='crimson', width=4, dash='dot'),
            mode='lines+markers+text',
            text=[f"{t_base:.1f}°C", f"{t_summit:.1f}°C", f"{t_leeward:.1f}°C"],
            textposition=["top right", "top center", "top left"]
        ), secondary_y=True)

        fig.update_xaxes(tickvals=[0, 50, 100], ticktext=["Chân núi Tây (Sườn đón gió ẩm)", "Đỉnh núi", "Chân núi Đông (Gió Phơn khô nóng)"])
        fig.update_yaxes(title_text="Độ cao địa hình (m)", secondary_y=False)
        fig.update_yaxes(title_text="Nhiệt độ không khí (°C)", secondary_y=True)
        fig.update_layout(title="Mặt cắt nhiệt độ theo độ cao qua dãy núi", height=450, legend=dict(orientation="h", y=1.1))

        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Giải thích địa lí:** Lên dốc 100m nhiệt độ giảm 0,6°C (do dãn nở đoạn nhiệt ngưng tụ hơi nước tạo mưa). Vượt qua đỉnh, khối khí khô trườn xuống 100m nhiệt độ tăng 1,0°C do nén đoạn nhiệt, tạo ra gió phơn khô nóng.")

# MÔ-ĐUN 3: BIỂU ĐỒ KHÍ HẬU & CHẨN ĐOÁN AI (BÀI 10) -----------------
elif menu == "3. Thực hành: Phân tích biểu đồ khí hậu & Chẩn đoán AI (Bài 10)":
    st.header("📊 Phân Tích Biểu Đồ Khí Hậu & Động Cơ Chuyên Gia Tự Động")
    st.caption("Bám sát yêu cầu cần đạt của Bài 10: Phân tích biểu đồ nhiệt độ - lượng mưa")

    climate_presets = {
        "Hà Nội (Việt Nam)": {
            "temp": [16.4, 17.0, 20.2, 23.7, 27.3, 28.8, 28.9, 28.2, 27.2, 24.6, 21.4, 18.2],
            "rain": [18, 26, 48, 90, 188, 240, 288, 318, 265, 130, 43, 21]
        },
        "U-pha (Liên bang Nga)": {
            "temp": [-14.5, -13.8, -7.0, 4.2, 13.5, 18.2, 20.1, 17.5, 11.2, 3.5, -5.2, -11.8],
            "rain": [35, 28, 25, 32, 45, 62, 70, 60, 52, 55, 48, 42]
        },
        "Va-len-ti-a (Ai-len)": {
            "temp": [7.2, 7.0, 8.1, 9.4, 11.5, 13.8, 15.2, 15.1, 13.8, 11.5, 9.2, 8.0],
            "rain": [158, 118, 112, 85, 88, 82, 95, 115, 128, 152, 155, 162]
        }
    }
    months = [f"T{i}" for i in range(1, 13)]
    selected_station = st.selectbox("Chọn trạm khí tượng chuẩn SGK hoặc tự nhập:", list(climate_presets.keys()) + ["Tùy biến dữ liệu trạm địa phương"])

    if selected_station != "Tùy biến dữ liệu trạm địa phương":
       t_data = climate_presets[selected_station]["temp"]
       r_data = climate_presets[selected_station]["rain"]
    else:
        st.write( "📝 **Bấm đúp chuột vào từng ô để nhập số liệu nhiệt độ &amp; lượng mưa" " 12 tháng:**" )
        # Khởi tạo bảng mẫu mặc định cho 12 tháng
        default_df = pd.DataFrame( {"Nhiệt độ (°C)": [20.0] * 12, "Lượng mưa (mm)": [100.0] * 12}, index=months, ).T
        # Hiển thị bảng tương tác cho phép sửa trực tiếp
        edited_df = st.data_editor(default_df, use_container_width=True)
        # Lấy dữ liệu người dùng vừa gõ vào
        t_data = edited_df.loc["Nhiệt độ (°C)"].values.astype(float).tolist()
        r_data = edited_df.loc["Lượng mưa (mm)"].values.astype(float).tolist()
    t_avg = np.mean(t_data)
    t_max, t_min = max(t_data), min(t_data)
    amp_t = t_max - t_min
    total_rain = sum(r_data)
    rainy_months = [months[i] for i, r in enumerate(r_data) if r >= 100]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=months, y=r_data, name="Lượng mưa (mm)", marker_color='rgb(55, 126, 184)'), secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=t_data, name="Nhiệt độ (°C)", line=dict(color='crimson', width=3), mode='lines+markers'), secondary_y=True)

    fig.update_yaxes(title_text="Lượng mưa (mm)", secondary_y=False, range=[0, max(r_data)*1.25])
    fig.update_yaxes(title_text="Nhiệt độ (°C)", secondary_y=True)
    fig.update_layout(title=f"Biểu đồ Khí hậu trạm {selected_station}", height=420)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nhiệt độ TB năm", f"{t_avg:.1f} °C")
    c2.metric("Biên độ nhiệt năm", f"{amp_t:.1f} °C")
    c3.metric("Tổng lượng mưa năm", f"{total_rain:.0f} mm")
    c4.metric("Số tháng mùa mưa (≥100mm)", f"{len(rainy_months)} tháng")

    st.subheader("🤖 Trợ lí Sư phạm Ảo: Chẩn đoán Kiểu Khí hậu")
    if t_min > 0 and amp_t < 10 and total_rain > 1000:
        diag_type = "Ôn đới hải dương (Ví dụ: Va-len-ti-a)"
        reason = [
            "Nhiệt độ ấm áp quanh năm, tháng lạnh nhất trên 0°C, biên độ nhiệt năm rất nhỏ (<10°C).",
            "Mưa phân bố dồi dào, đều khắp các tháng trong năm do ảnh hưởng gió Tây ôn đới và dòng biển nóng."
        ]
    elif t_min < -5 and amp_t > 25 and total_rain < 700:
        diag_type = "Ôn đới lục địa (Ví dụ: U-pha)"
        reason = [
            "Mùa đông rất lạnh giá sâu (tháng lạnh nhất < -10°C), biên độ nhiệt năm lớn (>25°C).",
            "Lượng mưa ít (<600mm), mưa chủ yếu vào mùa hạ do nằm sâu trong lục địa ít chịu ảnh hưởng của biển."
        ]
    elif t_avg > 20 and amp_t > 10 and total_rain > 1500:
        diag_type = "Nhiệt đới gió mùa (Ví dụ: Hà Nội)"
        reason = [
            "Nhiệt độ trung bình năm cao (>20°C), có mùa đông lạnh hạ nhiệt rõ nét.",
            "Lượng mưa lớn (>1500mm), phân mùa sâu sắc: mùa mưa từ T5 đến T10, mùa khô từ T11 đến T4 năm sau."
        ]
    else:
        diag_type = "Kiểu khí hậu chuyển tiếp hoặc trạm đặc thù"
        reason = ["Các chỉ số nhiệt - ẩm phản ánh sự kết hợp phức tạp từ độ cao và hoàn lưu cục bộ."]

    st.success(f"**Kết luận chẩn đoán:** {diag_type}")
    for r in reason:
        st.write(f"- {r}")

#  MÔ-ĐUN 4: THỦY QUYỂN (BÀI 13) 
elif menu == "4. Thủy quyển: Phân tích thủy chế Sông Hồng (Bài 13)":
    st.header("🌊 Thực Hành Phân Tích Thủy Chế Sông Hồng (Trạm Hà Nội)")
    st.caption("Bám sát nội dung Bảng 13 - SGK Địa lí 10 ")

    months = [f"T{i}" for i in range(1, 13)]
    flow = [1455, 1343, 1215, 1522, 2403, 4214, 7300, 7266, 5181, 3507, 2240, 1517]
    mean_flow = np.mean(flow)
    flood_months = [months[i] for i, q in enumerate(flow) if q > mean_flow]
    dry_months = [months[i] for i, q in enumerate(flow) if q <= mean_flow]

    fig = go.Figure()
    colors = ['crimson' if q > mean_flow else 'royalblue' for q in flow]
    fig.add_trace(go.Bar(x=months, y=flow, marker_color=colors, name="Lưu lượng tháng"))
    fig.add_trace(go.Scatter(
        x=months, y=[mean_flow]*12, mode='lines',
        line=dict(color='orange', width=3, dash='dash'),
        name=f"Lưu lượng TB năm ({mean_flow:.0f} m³/s)"
    ))
    fig.update_layout(title="Biểu đồ Lưu lượng nước trung bình tháng của Sông Hồng tại Hà Nội", height=420)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.error(f"**Mùa lũ:** Gồm các tháng **{', '.join(flood_months)}** (Lưu lượng > {mean_flow:.0f} m³/s). Đỉnh lũ vào T7 và T8.")
    with c2:
        st.info(f"**Mùa cạn:** Gồm các tháng **{', '.join(dry_months)}**. Tháng kiệt nhất là T3.")

#  MÔ-ĐUN 5: QUY LUẬT ĐAI CAO (BÀI 15, 18) 
elif menu == "5. Sinh quyển & Vỏ địa lí: Quy luật đai cao (Bài 15, 18)":
    st.header("🌲 Mô Phỏng Phân Bố Vành Đai Thực Vật Theo Độ Cao")
    st.caption("Khám phá quy luật phi địa đới và sự biến đổi thảm thực vật nhiệt đới ")

    user_elev = st.slider("Điều chỉnh độ cao khảo sát (m):", 0, 3200, 750, step=50)

    if user_elev < 600:
        zone = "Đai nhiệt đới chân núi"
        vegetation = "Rừng lá rộng thường xanh nhiệt đới ẩm, dây leo, bắp non"
        soil = "Đất feralit đỏ vàng, đất phù sa"
    elif user_elev <= 1600:
        zone = "Đai cận nhiệt đới gió mùa trên núi (thấp)"
        vegetation = "Rừng lá rộng á nhiệt đới, dẻ, re, thông"
        soil = "Đất feralit có mùn"
    elif user_elev <= 2600:
        zone = "Đai cận nhiệt đới gió mùa trên núi (cao)"
        vegetation = "Rừng hỗn hợp lá kim, pơmu, sa mu, đỗ quyên"
        soil = "Đất mùn thô trên núi"
    else:
        zone = "Đai ôn đới gió mùa trên núi (đỉnh cao >2600m)"
        vegetation = "Rừng lá kim nghèo nàn, bụi trúc lùn, cỏ đài nguyên"
        soil = "Đất mùn than bùn sơ khai"

    st.subheader(f"📍 Tại độ cao {user_elev} m:")
    st.subheader(f"📍 Tại độ cao khảo sát: {user_elev} m")
    st.info(f"🏔️ **VÀNH ĐAI CẢNH QUAN: {zone}")
    st.success(f"🌿 **THỰC VẬT TIÊU BIỂU: {vegetation}")
    st.warning(f"🪨 **NHÓM THỔ NHƯỠNG CHÍNH: {soil}")

# ----------------- MÔ-ĐUN 6: TRA CỨU & LUYỆN TẬP -----------------
elif menu == "6. Tra cứu thuật ngữ & Luyện tập tương tác":
    st.header("📖 Tra Cứu Thuật Ngữ Địa Lí 10 & Trắc Nghiệm Tương Tác")
    tab_lookup, tab_quiz = st.tabs(["🔍 Từ Điển Thuật Ngữ (SGK tr. 113)", "📝 Trắc Nghiệm Tư Duy"])

    with tab_lookup:
        glossary = {
            "Biển tiến": "Hiện tượng nước biển lấn vào lục địa do lục địa bị hạ thấp hoặc nước biển dâng .",
            "Biển thoái": "Hiện tượng biển rút khỏi lục địa do lục địa nâng lên hoặc nước biển hạ thấp .",
            "Gió địa phương": "Gió hình thành do điều kiện đặc biệt của địa hình và hoàn lưu khí quyển địa phương (như gió phơn, gió thung lũng) .",
            "Bùng nổ dân số": "Sự phát triển dân số vượt bậc về số lượng khi tỉ lệ sinh vẫn cao nhưng tỉ lệ tử giảm mạnh .",
            "Khí nhà kính": "Các khí trong khí quyển giữ nhiệt gây ra hiện tượng nóng lên toàn cầu (CO2, CH4, N2O, CFCs) .",
            "Quỳnh anh": "Là hs 12A1"
        }
        kw = st.text_input("Nhập thuật ngữ cần tìm kiếm:", value="")
        if kw.strip():
            found = False
            for term, desc in glossary.items():
                if kw.lower() in term.lower() or kw.lower() in desc.lower():
                    st.markdown(f"**📌 {term}:** {desc}")
                    found = True
            if not found:
                    st.warning( f"Không tìm thấy thuật ngữ phù hợp với từ khóa: '**{kw}**'" )
            else: # Gợi ý nhẹ khi ô tìm kiếm đang trống
                    st.info("💡 Hãy nhập từ khóa vào ô phía trên để bắt đầu tra cứu.")
    with tab_quiz:
        st.subheader("Câu hỏi vận dụng: Hiệu ứng phơn dãy Trường Sơn")
        ans = st.radio(
            "Câu thơ 'Trường Sơn Đông, Trường Sơn Tây / Bên nắng đốt, bên mưa quây' phản ánh tác động của loại gió nào? ",
            ["Gió mùa Đông Bắc", "Gió Tín phong Bán cầu Bắc", "Gió mùa Tây Nam (gây hiệu ứng phơn sườn Đông)", "Gió đất - gió biển"]
        )
        if st.button("Kiểm tra câu trả lời"):
            if ans == "Gió mùa Tây Nam (gây hiệu ứng phơn sườn Đông)":
                st.balloons()
                st.success("Chính xác! Gió mùa Tây Nam khi vượt qua sườn Trường Sơn sang bờ Đông bị mất ẩm, nén nhiệt trở nên khô nóng rát ")
            else:
                st.error("Chưa chính xác! Hãy ôn lại bài thực hành mô phỏng hiệu ứng Phơn ở Mô-đun 2.")

#  MÔ-ĐUN 7: TRẠM TRÒ CHƠI THƯ GIÃN
elif menu == "7. 🎮 Trạm trò chơi thư giãn & Giảm stress ":
    st.header("🎮 GeoArcade: Trạm Giải Trí & Giảm Căng Thẳng Địa Lí")
    st.markdown("""
    *Thư giãn tinh thần và tái tạo năng lượng sau các giờ học phân tích dữ liệu với các mini-game giáo dục tương tác nhẹ nhàng!*
    """)

    game_tab1, game_tab2, game_tab3 = st.tabs([
        "🔠 GeoWordle (Đoán Thuật Ngữ)",
        "✈️ Phi Công Xuyên Múi Giờ",
        "🌊 Thử Thách Điều Tiết Lũ Sông Hồng"
    ])

    #  MINI-GAME 1: GEOWORDLE  
    with game_tab1:
        st.subheader("Trò chơi 1: Đoán Thuật Ngữ Địa Lí 10 🌍")
        st.caption("Khám phá từ khóa bí ẩn được trích dẫn từ Bảng giải thích thuật ngữ SGK tr. 113 ")

        terms_bank = [
            {"word": "BIEN TIEN", "hint": "Hiện tượng nước biển dấn sâu vào đất liền do lục địa hạ thấp hoặc băng tan ."},
            {"word": "BIEN THOAI", "hint": "Hiện tượng nước biển rút ra xa khỏi lục địa do nâng mảng kiến tạo hoặc thời kì băng hà ."},
            {"word": "GIO PHON", "hint": "Loại gió khô nóng hình thành khi khối khí vượt qua sườn núi khuất gió "},
            {"word": "MACMA", "hint": "Vật chất quánh dẻo nóng chảy ở nhiệt độ cao trong lòng đất, phun trào tạo núi lửa ."},
            {"word": "KHI NHA KINH", "hint": "Các hợp chất khí trong khí quyển giữ nhiệt gây nên hiện tượng ấm lên toàn cầu ."}
        ]

        if "secret_idx" not in st.session_state:
            st.session_state.secret_idx = random.randint(0, len(terms_bank) - 1)
            st.session_state.attempts = 0

        target = terms_bank[st.session_state.secret_idx]

        st.info(f"💡 **Gợi ý:** {target['hint']}")
        st.write(f"Độ dài từ khóa: **{len(target['word'].replace(' ', ''))} chữ cái** (viết hoa không dấu)")

        user_guess = st.text_input("Nhập phán đoán của bạn:", key="wordle_input").strip().upper()

        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            if st.button("Đoán ngay 🎯"):
                st.session_state.attempts += 1
                if user_guess == target["word"]:
                    st.balloons()
                    st.success(f"🎉 XUẤT SẮC! Bạn đã đoán đúng từ khóa **{target['word']}** sau {st.session_state.attempts} lượt!")
                else:
                    st.error("Chưa chính xác rồi, hãy thử suy nghĩ lại gợi ý nhé!")

        with col_b2:
            if st.button("Đổi từ khác 🔄"):
                st.session_state.secret_idx = random.randint(0, len(terms_bank) - 1)
                st.session_state.attempts = 0
                st.rerun()

    #   MINI-GAME 2: TIME ZONE RUNNER  
    with game_tab2:
        st.subheader("Trò chơi 2: Chuyến Bay Xuyên Múi Giờ ✈️")
        st.caption("Rèn luyện phản xạ tính giờ quốc tế dựa trên Hình 5.2 - Bản đồ giờ Trái Đất SGK Địa lí 10 ")

        st.markdown("""
        **Tình huống điều phối chuyến bay:**
        * Máy bay Boeing cất cánh từ **Hà Nội (Múi giờ GMT +7)** lúc **08:00 sáng ngày 01/01** .
        * Thời gian bay hành trình: **12 tiếng**.
        * Điểm đến: **Luân Đôn (London - Múi giờ gốc GMT 0)** .
        """)

        player_time = st.slider("Theo giờ địa phương tại Luân Đôn, máy bay hạ cánh lúc mấy giờ?", 0, 23, 12)

        
        if st.button("Xác nhận hạ cánh 🛬"):
            correct_hour = (8 - 7 + 12) % 24  # 8h Hà Nội = 1h Luân Đôn. Bay 12h -> 13:00
            if player_time == correct_hour:
                st.snow()
                st.success(f"🏆 CHÍNH XÁC ! Lúc máy bay hạ cánh là đúng {correct_hour}:00 chiều cùng ngày tại Luân Đôn!")
            else:
                st.warning(f"Chưa chuẩn xác! Khi bay từ Hà Nội lúc 8h thì Luân Đôn mới là 1h sáng. Bay thêm 12h thì đáp án phải là {correct_hour}:00!")

    #  == MINI-GAME 3: ĐIỀU TIẾT LŨ SÔNG HỒNG  ==
    with game_tab3:
        st.subheader("Trò chơi 3: Trưởng Ban Chỉ Huy Hồ Thủy Điện Sông Hồng 🌊")
        st.caption("Thực tế hóa số liệu mùa lũ lưu lượng cực đại trạm Hà Nội (Bảng 13 SGK) ")

        st.markdown("""
        Vào tháng 7 và tháng 8, lưu lượng nước thượng nguồn đổ về đạt đỉnh hơn **7.200 m³/s** (mức an toàn chỉ khoảng 3.600 m³/s) .
        Nhiệm vụ của bạn là điều tiết tỉ lệ mở cửa xả tràn sao cho vừa cắt lũ an toàn cho hạ du vừa giữ đủ nước phát điện!
        """)

        dam_capacity = st.slider("Tỉ lệ mở cửa xả đáy hồ thủy điện (%):", 0, 100, 50, step=5)
        simulated_water_level = 7300 - (dam_capacity * 45)

        st.metric(
            label="Lưu lượng nước đổ dồn về hạ lưu Hà Nội",
            value=f"{simulated_water_level:.0f} m³/s",
            delta=f"{simulated_water_level - 3644:.0f} m³/s so với mức an toàn",
            delta_color="inverse"
        )

        if simulated_water_level > 5500:
            st.error("🚨 NGUY HIỂM: Nước lũ tràn đê bối! Cần tăng tỉ lệ xả/cắt lũ ngay!")
        elif simulated_water_level < 3000:
            st.warning("⚠️ CẢNH BÁO: Mở quá lớn làm cạn kiệt nguồn nước tích trữ của nhà máy điện mùa khô!")
        else:
            st.success("✅ THÀNH CÔNG: Bạn đã điều phối dòng chảy sông Hồng ở mức an toàn tuyệt đối!")
if menu == "8. ôn tập, kiểm tra":
    st.header("Luyện đề và các đề kiểm tra tham khảo")
    st.markdown("""
    *Nhằm mục đích ôn lại kiến thức đã học*
    """)
   
    kt_tab1, kt_tab2 = st.tabs( ["📚 Ôn tập theo chủ đề (13 Chương)", "⏱️ Đề thi tham khảo"] )
    with kt_tab1:
        # 1. Bảng ánh xạ 13 chương sang các file .txt tương ứng
        chuong_mapping = {
            "Chương 1: Sử dụng bản đồ": "c1.txt",
            "Chương 2: Trái Đất": "c2.txt",
            "Chương 3: Thạch quyển": "c3.txt",
            "Chương 4: Khí quyển": "c4.txt",
            "Chương 5: Thủy quyển": "c5.txt",
            "Chương 6: Sinh quyển": "c6.txt",
            "Chương 7: Một số quy luật của vỏ địa lí": "c7.txt",
            "Chương 8: Địa lí dân cư": "c8.txt",
            "Chương 9: Các nguồn lực &amp; chỉ số phát triển kinh tế": (
                "c9.txt"
            ),  
            "Chương 10: Địa lí ngành nông nghiệp, lâm nghiệp, thủy sản": "c10.txt",
            "Chương 11: Địa lí ngành công nghiệp": "c11.txt",
            "Chương 12: Địa lí ngành dịch vụ": "c12.txt",
            "Chương 13: Phát triển bền vững và tăng trưởng xanh": "c13.txt",
        }

        
# 2. Hộp chọn chương
    chuong_duoc_chon = st.selectbox(
        "📖 Chọn chương kiến thức cần ôn tập:", list(chuong_mapping.keys())
    )
    st.markdown(f"### 🎯 Nội dung ôn tập: **{chuong_duoc_chon}**")

    # 3. Lấy tên tệp và đọc đồng thời cả 3 phần câu hỏi
    ten_file = chuong_mapping[chuong_duoc_chon]
    ds_mcq, ds_tf, ds_sa = doc_file_chuong_toan_dien(ten_file)

    if ds_mcq or ds_tf or ds_sa:
      # Chia thành 3 tab tương ứng 3 phần theo định dạng chuẩn
      tab_mcq, tab_tf, tab_sa = st.tabs([
          f"🔘 Phần I: 4 Lựa chọn ({len(ds_mcq)} câu)",
          f"🎯 Phần II: Đúng / Sai ({len(ds_tf)} câu)",
          f"✍️ Phần III: Trả lời ngắn ({len(ds_sa)} câu)",
      ])

      # --- PHẦN I: TRẮC NGHIỆM 4 LỰA CHỌN (GIỮ NGUYÊN GIAO DIỆN CỦA BẠN) ---
      with tab_mcq:
        if ds_mcq:
          st.caption(
              f"Đang hiển thị **{len(ds_mcq)}** câu hỏi trắc nghiệm từ tệp"
              f" `{ten_file}`:"
          )
          for idx, q in enumerate(ds_mcq):
            st.markdown(f"**Câu {idx + 1}:** {q['cau_hoi']}")
            user_ans = st.radio(
                "Chọn đáp án:",
                q["lua_chon"],
                index=None,
                key=f"mcq_{ten_file}_{idx}",
                label_visibility="collapsed",
            )
            if user_ans:
              if user_ans.startswith(q["dap_an"]):
                st.success(f"🎉 **Chính xác!** {q['giai_thich']}")
              else:
                st.error(
                    f"❌ **Chưa đúng!** Đáp án đúng là **{q['dap_an']}**."
                    f" {q['giai_thich']}"
                )
            st.markdown("---")
        else:
          st.info("Chưa có câu hỏi nhiều lựa chọn trong tệp này.")

      # --- PHẦN II: TRẮC NGHIỆM ĐÚNG / SAI ---
      with tab_tf:
        if ds_tf:
          for idx, q in enumerate(ds_tf):
            st.subheader(f"Câu {idx + 1}: {q['tieu_de']}")
            if q["thong_tin"]:
              st.info(f"**Tư liệu:** {q['thong_tin']}")

            for sub_idx, sub in enumerate(q["y"]):
              c_txt, c_opt = st.columns([3.5, 1.5])
              with c_txt:
                st.markdown(f"**{sub['label']}** {sub['statement']}")
              with c_opt:
                user_choice = st.radio(
                    "Chọn:",
                    ["Đúng", "Sai"],
                    index=None,
                    horizontal=True,
                    key=f"tf_{ten_file}_{idx}_{sub_idx}",
                    label_visibility="collapsed",
                )

              if user_choice:
                if user_choice == sub["ans"]:
                  st.success(
                      f"✅ **Ý {sub['label']} ĐÚNG!** (Đáp án: {sub['ans']}) -"
                      f" {sub['exp']}"
                  )
                else:
                  st.error(
                      f"❌ **Ý {sub['label']} CHƯA ĐÚNG!** (Đáp án:"
                      f" {sub['ans']}) - {sub['exp']}"
                  )
            st.markdown("---")
        else:
          st.info("Chưa có câu hỏi Đúng / Sai trong tệp này.")

      # --- PHẦN III: TRẢ LỜI NGẮN ---
      with tab_sa:
        if ds_sa:
          st.caption(
              "Học sinh tính toán và nhập đáp án ngắn (số nguyên hoặc số thập"
              " phân) vào ô bên dưới:"
          )
          for idx, q in enumerate(ds_sa):
            st.markdown(f"**Câu {idx + 1}:** {q['cau_hoi']}")
            c_in, c_chk = st.columns([4, 1])
            with c_in:
              user_text = st.text_input(
                  f"Nhập câu trả lời cho Câu {idx + 1}:",
                  key=f"sa_in_{ten_file}_{idx}",
                  placeholder="Ví dụ: 32 hoặc 12.5...",
                  label_visibility="collapsed",
              )
            with c_chk:
              btn_check = st.button("Kiểm tra", key=f"sa_btn_{ten_file}_{idx}")

            if user_text.strip() or btn_check:
              if user_text.strip():
                ans_clean = (
                    user_text.strip()
                    .replace(" ", "")
                    .replace(",", ".")
                    .lower()
                    .replace("°c", "")
                    .replace("độ", "")
                    .replace("m", "")
                    .replace("mm", "")
                )
                correct_clean = (
                    q["dap_an"]
                    .strip()
                    .replace(" ", "")
                    .replace(",", ".")
                    .lower()
                    .replace("°c", "")
                    .replace("độ", "")
                    .replace("m", "")
                    .replace("mm", "")
                )
                if ans_clean == correct_clean:
                  st.success(
                      f"🎉 **Chính xác!** Đáp án là **{q['dap_an']}**.\n\n📌"
                      f" **Giải thích:** {q['giai_thich']}"
                  )
                else:
                  st.error(
                      f"❌ **Chưa chính xác!** Đáp án đúng là"
                      f" **{q['dap_an']}**.\n\n📌 **Hướng dẫn giải:**"
                      f" {q['giai_thich']}"
                  )
              else:
                st.warning("Vui lòng nhập câu trả lời trước khi bấm kiểm tra.")
            st.markdown("---")
        else:
          st.info("Chưa có câu hỏi trả lời ngắn trong tệp này.")

    else:
      st.warning(
          f"⚠️ Chưa tìm thấy tệp `{ten_file}` trong thư mục `D:\\KHKT`. Hãy đảm"
          " bảo bạn đã đặt tệp câu hỏi vào cùng thư mục với `app.py`!"
      )

    with kt_tab2:
        st.subheader("⏱️ Đề thi tham khảo tổng hợp")
        st.info("Bộ đề tổng hợp giữa kỳ và cuối kỳ đang được cập nhật vào hệ thống.")


    