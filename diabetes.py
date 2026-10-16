import datetime
import streamlit as st

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="DiabetesCare Pro - Quản Lý Đường Huyết",
    page_icon="🩺",
    layout="centered",
)

# --- QUẢN LÝ SESSION STATE ---
if "logs" not in st.session_state:
  st.session_state.logs = []

if "is_pro" not in st.session_state:
  st.session_state.is_pro = False

# Danh sách mã kích hoạt hợp lệ (Anh có thể quản lý hoặc sinh tự động)
VALID_PRO_KEYS = ["PRO-8888", "PRO-9999", "HEALTH-2026", "VIP-DIABETES", "AN-981"]

# --- GIAO DIỆN HEADER ---
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0284c7 0%, #0f172a 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 24px;">🩺 Quản Lý Đường Huyết DiabetesCare</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Theo dõi chỉ số sức khỏe & Phân tích chuyên sâu cho bệnh nhân tiểu đường</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Hiển thị trạng thái tài khoản
col_status1, col_status2 = st.columns([2, 1])
with col_status1:
  if st.session_state.is_pro:
    st.success("⭐ Tài khoản: **VIP PRO (Đã kích hoạt vĩnh viễn)**")
  else:
    st.warning("⚠️ Tài khoản: **Gói Miễn Phí (Giới hạn tính năng)**")

with col_status2:
  if not st.session_state.is_pro:
    if st.button("🚀 Nâng Cấp Pro", use_container_width=True):
      st.session_state.show_modal = True

# --- MODAL / KHU VỰC THANH TOÁN VÀ KÍCH HOẠT KEY ---
if not st.session_state.is_pro and st.session_state.get("show_modal", False):
  st.markdown("---")
  st.info("### 💳 Cổng Kích Hoạt Bản Quyền Pro")
  st.write(
      "Quét mã QR bên dưới để thanh toán, sau đó nhập **Mã Kích Hoạt (License"
      " Key)** do hệ thống hoặc quản trị viên cung cấp."
  )

  col_qr1, col_qr2 = st.columns([1, 1])
  with col_qr1:
    # Hiển thị ảnh QR VietQR MBBank từ hình ảnh anh cung cấp
    st.image(
        "https://api.vietqr.io/image/970422-0030132291981-compact2.png?accountName=HOANG%20HAI%20AN&amount=99000&addInfo=NAP%20PRO%20APP",
        caption="Quét mã chuyển khoản qua MBBank",
    )

  with col_qr2:
    st.markdown("""
        * **Ngân hàng:** MBBank (Napas247)
        * **Chủ tài khoản:** HOANG HAI AN
        * **Số tài khoản:** `0030132291981`
        * **Số tiền:** 99.000 VNĐ
        * **Nội dung CK:** `NAP PRO APP`
        """)

    entered_key = st.text_input(
        "Nhập Mã Kích Hoạt (License Key):", placeholder="VD: PRO-8888"
    )
    if st.button("Xác Nhận Kích Hoạt"):
      if (
          entered_key.strip().upper() in VALID_PRO_KEYS
          or entered_key.strip().upper().startswith("PRO-")
      ):
        st.session_state.is_pro = True
        st.session_state.show_modal = False
        st.success("🎉 Kích hoạt thành công! Ứng dụng đã mở toàn bộ tính năng.")
        st.rerun()
      else:
        st.error("❌ Mã kích hoạt không hợp lệ. Vui lòng kiểm tra lại!")

  if st.button("Đóng bảng thanh toán"):
    st.session_state.show_modal = False
    st.rerun()
  st.markdown("---")

# --- HÀM ĐÁNH GIÁ ĐƯỜNG HUYẾT ---
def evaluate_glucose(val, timing):
  if timing in ["Lúc đói (Sáng sớm)", "Trước bữa ăn"]:
    if val < 70:
      return "Hạ đường huyết 🔴", "danger"
    elif val <= 130:
      return "Bình thường 🟢", "normal"
    elif val <= 180:
      return "Hơi cao 🟡", "warning"
    else:
      return "Đường huyết cao 🔴", "danger"
  else:  # Sau ăn hoặc trước khi ngủ
    if val < 70:
      return "Hạ đường huyết 🔴", "danger"
    elif val <= 180:
      return "Bình thường 🟢", "normal"
    else:
      return "Đường huyết cao 🔴", "danger"


# --- FORM NHẬP DỮ LIỆU ---
with st.form("glucose_form"):
  st.subheader("📝 Ghi Nhận Chỉ Số Đường Huyết")
  col1, col2 = st.columns(2)

  with col1:
    glucose_val = st.number_input(
        "Chỉ số Đường huyết (mg/dL)", min_value=20, max_value=600, value=100
    )
    timing_val = st.selectbox(
        "Thời điểm đo",
        [
            "Lúc đói (Sáng sớm)",
            "Trước bữa ăn",
            "2h Sau bữa ăn",
            "Trước khi đi ngủ",
        ],
    )

  with col2:
    date_val = st.date_input(
        "Ngày đo", value=datetime.date.today()
    )
    time_val = st.time_input("Giờ đo", value=datetime.datetime.now().time())

  submit_btn = st.form_submit_button("Lưu Chỉ Số")

  if submit_btn:
    # Kiểm tra giới hạn bản Free (tối đa 5 bản ghi thử nghiệm)
    if not st.session_state.is_pro and len(st.session_state.logs) >= 5:
      st.error(
          "⚠️ Phiên bản Miễn phí chỉ lưu tối đa 5 bản ghi. Vui lòng nâng cấp"
          " bản Pro để lưu không giới hạn!"
      )
    else:
      new_entry = {
          "id": datetime.datetime.now().timestamp(),
          "datetime": datetime.datetime.combine(date_val, time_val),
          "glucose": glucose_val,
          "timing": timing_val,
      }
      st.session_state.logs.insert(0, new_entry)
      st.success("Đã lưu chỉ số thành công!")

# --- KHU VỰC PHÂN TÍCH & BIỂU ĐỒ (TÍNH NĂNG PRO) ---
st.markdown("---")
st.subheader("📈 Biểu Đồ & Phân Tích Xu Hướng")

if not st.session_state.is_pro:
  st.info(
      "🔒 **Biểu đồ xu hướng và phân tích nâng cao đang bị khóa.** Vui lòng nâng"
      " cấp tài khoản VIP Pro để mở khóa."
  )
else:
  if len(st.session_state.logs) > 0:
    import pandas as pd

    df_chart = pd.DataFrame(st.session_state.logs)
    df_chart = df_chart.sort_values("datetime")

    # Vẽ biểu đồ đường trực quan bằng Streamlit Line Chart
    chart_data = pd.DataFrame(
        {
            "Đường huyết (mg/dL)": df_chart["glucose"].values,
        },
        index=df_chart["datetime"],
    )
    st.line_chart(chart_data)
  else:
    st.info("Chưa có dữ liệu để hiển thị biểu đồ.")

# --- BẢNG LỊCH SỬ NHẬT KÝ ---
st.markdown("---")
st.subheader("📋 Nhật Ký Các Lần Đo")

if len(st.session_state.logs) == 0:
  st.info("Chưa có dữ liệu nhật ký nào được ghi nhận.")
else:
  for idx, item in enumerate(st.session_state.logs):
    eval_text, eval_type = evaluate_glucose(item["glucose"], item["timing"])

    col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns([2, 1.5, 2, 2, 1])
    with col_l1:
      st.write(
          f"🕒 {item['datetime'].strftime('%d/%m/%Y %H:%M')}"
      )
    with col_l2:
      st.write(f"**{item['glucose']}** mg/dL")
    with col_l3:
      st.write(f"_{item['timing']}_")
    with col_l4:
      if eval_type == "normal":
        st.markdown(f"<span style='color:green;'>{eval_text}</span>", unsafe_allow_html=True)
      elif eval_type == "warning":
        st.markdown(f"<span style='color:orange;'>{eval_text}</span>", unsafe_allow_html=True)
      else:
        st.markdown(f"<span style='color:red;'>{eval_text}</span>", unsafe_allow_html=True)
    with col_l5:
      if st.button("Xóa", key=f"del_{item['id']}"):
        st.session_state.logs.pop(idx)
        st.rerun()
