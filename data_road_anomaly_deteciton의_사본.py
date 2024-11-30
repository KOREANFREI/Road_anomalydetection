# -*- coding: utf-8 -*-
"""Data_road_anomaly_deteciton의 사본

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cSrs65U0UgxDoX0QNhcjckh4TxyOiFQ_

##Anomaly Detection을 통한 도로 내 이상탐지

## 구글 drive 연결 및 data directory연결
"""

from google.colab import drive
drive.mount('/content/drive')  # Google Drive 마운트

# 올바른 data_dir 경로를 설정
data_dir = '/content/drive/My Drive/data_road'  # 실제 데이터셋 위치에 맞게 수정

"""## data 파일 내 구조 확인 및 폴더 확인"""

import os

# data_road 폴더가 존재하는지 확인
if os.path.exists(data_dir):
    print("data_road 폴더가 존재합니다.")
else:
    print("data_road 폴더를 찾을 수 없습니다.")

# training 폴더 내 구조 확인
training_dir = os.path.join(data_dir, 'training')
if os.path.exists(training_dir):
    print("training 폴더가 존재합니다.")
    print("training 폴더 내용:", os.listdir(training_dir))
else:
    print("training 폴더를 찾을 수 없습니다.")

# training/image_2 폴더 확인
image_2_dir = os.path.join(training_dir, 'image_2')
if os.path.exists(image_2_dir):
    print("image_2 폴더 내용:", os.listdir(image_2_dir))
else:
    print("image_2 폴더를 찾을 수 없습니다.")

"""## 검출하고자 하는 도로영역 분할부분 출력"""

import cv2
import numpy as np
import os
from google.colab.patches import cv2_imshow

def segment_road(image):
    """
    이미지에서 도로 영역을 분할합니다.

    Args:
      image: 입력 이미지.

    Returns:
      도로 영역 마스크.
    """
    # HSV 색 공간으로 변환
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 도로 색상 범위 지정 (회색, 검정)
    lower_gray = (0, 0, 25)
    upper_gray = (180, 80, 250)

    # 색상 범위에 해당하는 픽셀 마스크 생성
    mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # 형태학적 연산 (선택 사항)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask

# 이미지 디렉토리 경로
image_dir = '/content/drive/My Drive/data_road/training/image_2'

# 디렉토리 내의 모든 이미지 파일 처리
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # 이미지 로드
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"이미지를 읽을 수 없습니다: {filename}")
            continue

        # 도로 영역 분할
        road_mask = segment_road(image)

        # 색상 정의 (예: 파란색)
        color = (255, 0, 0)  # BGR 순서

        # 마스킹된 이미지 생성 (색상 적용)
        colored_mask = np.zeros_like(image)
        colored_mask[road_mask > 0] = color

        # 결과 출력 (원본 이미지와 색칠된 마스크를 합쳐서 출력)
        result = cv2.addWeighted(image, 0.7, colored_mask, 0.3, 0)
        cv2_imshow(result)

def load_and_preprocess_image(img_path, img_size=(256, 256)):
    """
    이미지를 로드하고 전처리합니다.

    Args:
        img_path (str): 이미지 파일 경로.
        img_size (tuple): (width, height) 크기로 이미지를 조정. 기본값은 (256, 256).

    Returns:
        tuple: 전처리된 이미지 배열과 레이블.
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"이미지를 읽을 수 없습니다: {img_path}")
            return None, None

        # 이미지 높이, 너비 가져오기
        height, width = img.shape[:2]

        # 이미지 아래 절반 자르기
        cropped_img = img[height//2:height, 0:width]

        # 이미지 크기 조정
        img_resized = cv2.resize(cropped_img, img_size)

        # --- 도로 마스크 적용 ---
        road_mask = segment_road(img_resized)  # 도로 영역 분할 함수 호출
        masked_img = cv2.bitwise_and(img_resized, img_resized, mask=road_mask)  # 마스크 적용

        return masked_img, 1

    except Exception as e:
        print(f"오류 발생 {img_path}: {e}")
        return None, None


def preprocess_training_images(data_dir, img_size=(512, 256)):
    """
    training 폴더의 이미지 데이터를 전처리합니다.

    Args:
        data_dir (str): 데이터 폴더 경로.
        img_size (tuple): (width, height) 크기로 이미지를 조정. 기본값은 (256, 256).

    Returns:
        tuple: 전처리된 이미지 배열과 레이블 배열.
    """
    images = []
    labels = []
    detected_image_names = []  # 원이 검출된 이미지의 이름을 저장할 리스트
    total_detected_circles = 0  # 검출된 원의 총 개수
    detected_image_count = 0  # 원이 검출된 이미지의 개수

    split_dir = os.path.join(data_dir, "training")
    image_dir = os.path.join(split_dir, "image_2")  # 'image_2' 디렉토리 사용

    if not os.path.exists(image_dir):
        print(f"경고: 디렉토리를 찾을 수 없습니다: {image_dir}")
        return np.array(images), np.array(labels)

    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(image_dir, filename)

            # 이미지 로드 및 전처리
            preprocessed_img, label = load_and_preprocess_image(img_path, img_size)
            if preprocessed_img is None:
                continue

            # 포트홀 검출
            detected_img, detected_circles = detect_potholes(preprocessed_img)  # 마스크된 이미지 사용

            if detected_circles > 0:
                detected_image_names.append(filename)  # 검출된 이미지 이름 저장
                detected_image_count += 1  # 원이 검출된 이미지의 개수 증가
                total_detected_circles += detected_circles  # 검출된 원 개수 누적
                images.append(detected_img)  # 원이 그려진 이미지 추가
                labels.append(1)  # training 데이터는 레이블 1로 설정
            else:
                images.append(preprocessed_img)  # 원본 이미지 추가
                labels.append(0)  # 원이 검출되지 않은 경우 0 추가

    # 원 검출 결과 출력
    print(f"원이 검출된 이미지 수: {detected_image_count}")
    print(f"원이 검출된 이미지 목록: {detected_image_names}")
    print(f"총 검출된 원의 개수: {total_detected_circles}")

    return np.array(images), np.array(labels)

def detect_potholes(img):
    """
    이미지에서 포트홀(원)을 검출합니다.

    Args:
        img: 입력 이미지.

    Returns:
        tuple: 포트홀 검출 결과 이미지와 검출된 원의 개수.
    """
    # 이미지 복사
    img_with_circles = img.copy()

    # 가우시안 블러 처리
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # Canny Edge Detection 적용
    edges = cv2.Canny(blurred, 50, 150)

    # Hough Circle Transform을 사용하여 원 검출
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=10, maxRadius=50)

    detected_circles = 0  # 검출된 원의 개수

    # 원 그리기
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        detected_circles = len(circles)  # 검출된 원의 개수 저장
        for (x, y, r) in circles:
            # 원 주위에 초록색 원 그리기
            cv2.circle(img_with_circles, (x, y), r, (0, 255, 0), 4)

    return img_with_circles, detected_circles  # 원이 그려진 이미지 반환

def load_and_preprocess_image(img_path, img_size=(256, 256)):
    """
    이미지를 로드하고 전처리합니다.

    Args:
        img_path (str): 이미지 파일 경로.
        img_size (tuple): (width, height) 크기로 이미지를 조정. 기본값은 (256, 256).

    Returns:
        tuple: 전처리된 이미지 배열과 레이블.
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"이미지를 읽을 수 없습니다: {img_path}")
            return None, None

        # 이미지 높이, 너비 가져오기
        height, width = img.shape[:2]

        # 이미지 아래 절반 자르기
        cropped_img = img[height//2:height, 0:width]

        # 이미지 크기 조정
        img_resized = cv2.resize(cropped_img, img_size)

        # --- 도로 마스크 적용 ---
        road_mask = segment_road(img_resized)  # 도로 영역 분할 함수 호출
        masked_img = cv2.bitwise_and(img_resized, img_resized, mask=road_mask)  # 마스크 적용

        return masked_img, 1

    except Exception as e:
        print(f"오류 발생 {img_path}: {e}")
        return None, None

def preprocess_training_images(data_dir, img_size=(512, 256)):
    """
    training 폴더의 이미지 데이터를 전처리합니다.

    Args:
        data_dir (str): 데이터 폴더 경로.
        img_size (tuple): (width, height) 크기로 이미지를 조정. 기본값은 (256, 256).

    Returns:
        tuple: 전처리된 이미지 배열과 레이블 배열.
    """
    images = []
    labels = []
    detected_image_names = []  # 원이 검출된 이미지의 이름을 저장할 리스트
    total_detected_circles = 0  # 검출된 원의 총 개수
    detected_image_count = 0  # 원이 검출된 이미지의 개수

    split_dir = os.path.join(data_dir, "training")
    image_dir = os.path.join(split_dir, "image_2")  # 'image_2' 디렉토리 사용

    if not os.path.exists(image_dir):
        print(f"경고: 디렉토리를 찾을 수 없습니다: {image_dir}")
        return np.array(images), np.array(labels)

    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(image_dir, filename)

            # 이미지 로드 및 전처리
            preprocessed_img, label = load_and_preprocess_image(img_path, img_size)
            if preprocessed_img is None:
                continue

            # 포트홀 검출
            detected_img, detected_circles = detect_potholes(preprocessed_img)  # 마스크된 이미지 사용

            if detected_circles > 0:
                detected_image_names.append(filename)  # 검출된 이미지 이름 저장
                detected_image_count += 1  # 원이 검출된 이미지의 개수 증가
                total_detected_circles += detected_circles  # 검출된 원 개수 누적
                images.append(detected_img)  # 원이 그려진 이미지 추가
                labels.append(1)  # training 데이터는 레이블 1로 설정

                # 원이 검출된 이미지 출력
                cv2_imshow(detected_img)
                print(filename) # 이미지 이름 출력

            else:
               images.append(preprocessed_img) # 원본 이미지 추가
               labels.append(0) # 원이 검출되지 않은 경우 0 추가


    # 원 검출 결과 출력
    print(f"원이 검출된 이미지 수: {detected_image_count}")
    print(f"원이 검출된 이미지 목록: {detected_image_names}")
    print(f"총 검출된 원의 개수: {total_detected_circles}")

    return np.array(images), np.array(labels)

# preprocess_training_images 함수를 호출하여 이미지 전처리 및 포트홀 검출 수행
images, labels = preprocess_training_images(data_dir)