import os

import streamlit as st
from PIL import Image

from screenshot_detector import detect_folder


def run_detection(folder_path="images/test"):
    """
    지정된 폴더의 이미지에 대해 스크린샷 감지 실행
    """
    output_file = "detection_results.tsv"
    result = detect_folder(folder_path, nprocess=4, output=output_file)
    return result


def display_image_analysis(img_path, line_count, is_screenshot):
    """각 이미지에 대한 분석 결과를 표시하는 함수"""
    st.markdown(f"### 이미지: {os.path.basename(img_path)}")

    col1, col2 = st.columns(2)
    img = Image.open(img_path)
    width, height = img.size

    with col1:
        new_height = 300
        new_width = int(width * (new_height / height))
        st.image(img, width=new_width)

    with col2:
        st.write(f"**파일 경로:** {img_path}")
        st.write(f"**수평 라인 수:** {line_count}")
        if is_screenshot:
            st.markdown("**판독 결과:** ✅ 스크린샷입니다")
        else:
            st.markdown("**판독 결과:** ❌ 스크린샷이 아닙니다")

        st.write(f"**이미지 크기:** {width} x {height} 픽셀")
        st.write(f"**파일 크기:** {os.path.getsize(img_path) / 1024:.2f} KB")

    st.markdown("---")


def main():
    st.set_page_config(layout="wide")
    st.title("Screenshot Detector Demo")
    st.markdown(
        """
    ## 소개
    이 도구는 이미지에서 수평 가장자리를 감지하여 스크린샷인지 아닌지 판단합니다.
    
    원리:
    1. 이미지를 그레이스케일로 변환
    2. 수평 가장자리 감지 필터 적용
    3. 수평 가장자리 수를 세어 스크린샷 여부 결정
    """
    )

    # 사용자가 폴더 경로를 입력할 수 있도록 텍스트 입력 추가
    folder_path = st.text_input("이미지 폴더 경로를 입력하세요", value="images/test")
    threshold = 1

    if st.button("스크린샷 감지 실행") or True:
        with st.spinner("감지 진행 중..."):
            results = run_detection(folder_path)

        if results is None:
            st.error("이미지 폴더를 찾을 수 없습니다.")
            return

        st.success("감지 완료!")

        if list(results.columns) == [0, 1, 2]:
            results.columns = ["인덱스", "이미지 경로", "수평 라인 수"]
        st.write(results)

        results["스크린샷 여부"] = results["수평 라인 수"] >= threshold
        screenshot_count = results["스크린샷 여부"].sum()
        col1, col2 = st.columns(2)
        col1.metric("감지된 스크린샷 수", screenshot_count)
        col2.metric("전체 이미지 수", len(results))

        st.write(f"기준: 수평 라인 수 >= {threshold}인 경우 스크린샷으로 판단")
        st.subheader("이미지 분석 결과")
        st.subheader("")

        for _, row in results.iterrows():
            img_path = row["이미지 경로"]
            line_count = row["수평 라인 수"]
            is_screenshot = row["스크린샷 여부"]
            display_image_analysis(img_path, line_count, is_screenshot)


if __name__ == "__main__":
    main()
