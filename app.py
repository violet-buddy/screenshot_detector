import base64
import os
import time

import cv2
import streamlit as st
from PIL import Image

from screenshot_detector import detect_folder


def render_img_html(image_b64):
    st.markdown(
        f"<img style='max-width: 100%;max-height: 300px;' src='data:image/png;base64, {image_b64}'/>",
        unsafe_allow_html=True,
    )


def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    _, encoded_image = cv2.imencode(".png", image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image


def display_one_image(row):
    img_path = row["이미지 경로"]
    line_count = row["수평 라인 수"]
    is_screenshot = row["스크린샷 여부"]

    col1, col2 = st.columns(2)
    img = Image.open(img_path)
    width, height = img.size
    with col1:
        render_img_html(image_to_base64(img_path))
    with col2:
        st.write(f"이미지: {os.path.basename(img_path)}")
        st.write(f"**파일 경로:** {img_path}")
        # st.write(f"**수평 라인 수:** {line_count}")
        # if is_screenshot:
        #     st.markdown("**판독 결과:** ✅ 스크린샷입니다")
        # else:
        #     st.markdown("**판독 결과:** ❌ 스크린샷이 아닙니다")
        st.write(f"**이미지 크기:** {width} x {height} 픽셀")
        st.write(f"**파일 크기:** {os.path.getsize(img_path) / 1024:.2f} KB")
    st.markdown("---")


def display_image_analysis(results):
    col_sshot, col_nonsshot = st.columns(2)
    col_sshot.subheader("✅ 스크린샷")
    col_nonsshot.subheader("📷 스크린샷이 아닌 사진")
    for _, row in results.iterrows():
        is_screenshot = row["스크린샷 여부"]
        if is_screenshot:
            with col_sshot:
                display_one_image(row)
        else:
            with col_nonsshot:
                display_one_image(row)


def introduction():
    st.set_page_config(layout="wide")
    st.title("Screenshot Detector Demo")
    st.markdown("""### 소개\n 이미지가 스크린샷인지 아닌지 판단합니다.""")


def run_detection(folder_path="images/test"):
    """지정된 폴더의 이미지에 대해 스크린샷 감지 실행"""
    output_file = "detection_results.tsv"

    start_time = time.time()
    with st.spinner("감지 진행 중..."):
        results = detect_folder(folder_path, nprocess=4, output=output_file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    st.success(f"감지 완료! (소요 시간: {elapsed_time:.2f}초)")
    if list(results.columns) == [0, 1, 2]:
        results.columns = ["인덱스", "이미지 경로", "수평 라인 수"]
    st.write(results)
    return results


def display_summary(results):
    col1, col2 = st.columns(2)
    threshold = 1
    results["스크린샷 여부"] = results["수평 라인 수"] >= threshold
    col1.metric("감지된 스크린샷 수", results["스크린샷 여부"].sum())
    col2.metric("전체 이미지 수", len(results))
    st.markdown("---")
    # st.write(f"기준: 수평 라인 수 >= {threshold}인 경우 스크린샷으로 판단")


def main():
    introduction()
    folder_path = st.text_input("이미지 폴더 경로를 입력하세요", value="images/test")
    results = run_detection(folder_path)
    display_summary(results)
    display_image_analysis(results)


if __name__ == "__main__":
    main()
