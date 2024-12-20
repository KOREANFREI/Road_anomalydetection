###    training 폴더의 이미지 데이터를 전처리합니다.

```python
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
```

``
