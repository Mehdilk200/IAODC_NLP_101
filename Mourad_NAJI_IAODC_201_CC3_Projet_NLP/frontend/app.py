import streamlit as st
import requests

st.set_page_config(page_title="Stylist Chatbot", page_icon="🧥")
st.title("🧥 Stylist Chatbot (MVP)")

msg = st.text_area(
    "كتب شنو باغي (مثال: عرس فالشتا بميزانية 800dh وبغيت شي حاجة رسمية):",
    height=120
)

num = st.slider("عدد الصور", 3, 12, 6)

if st.button("اقترح outfits + صور"):
    if not msg.strip():
        st.warning("كتب رسالة أولا.")
    else:
        try:
            r = requests.post(
                "http://127.0.0.1:8000/api/v1/images",
                json={"query": msg, "num": int(num)},
                timeout=20
            )
            data = r.json()

            st.subheader("🖼 صور مقترحة:")
            images = data.get("images", [])
            if not images:
                st.info("ما لقيتش صور، جرّب وصف أوضح (مثال: men winter wedding navy suit).")
            else:
                for im in images:
                    st.markdown(f"**{im.get('title','')}**")
                    if im.get("thumbnail"):
                        st.image(im["thumbnail"], use_container_width=True)
                    if im.get("link"):
                        st.markdown(im["link"])

        except Exception as e:
            st.error(f"وقع مشكل فالاتصال بالـ API: {e}")