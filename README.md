# Video Recorder

OpenCV를 이용해 웹캠/카메라 영상을 미리보기(Preview)하고, 필요한 구간만 녹화(Record)하거나 사진으로 캡처할 수 있는 비디오 레코더입니다.

## 주요 기능

- **PREVIEW / RECORD 모드**
  - 카메라 라이브 영상 표시
  - `SPACE` 키로 Preview ↔ Record 모드 전환
  - 녹화 중에는 좌측 상단에 **빨간 점 + 일시정지/재생 아이콘 + 경과 시간** 표시
- **영상 파일 저장**
  - OpenCV `VideoWriter`를 사용해 `.mp4` 파일로 저장
  - `recordings/record_YYYYMMDD_HHMMSS.mp4` 형식으로 자동 파일명 생성
  - 과제 요구사항에 맞게, 영상은 소리 없이(무음) 저장
- **스냅샷(사진 캡처) 기능**
  - Preview 상태이든, 녹화 중이든 언제든지 한 장씩 캡처
  - 캡처 시 화면이 잠깐 하얗게 번쩍이는 플래시 효과
  - `snapshots/snapshot_YYYYMMDD_HHMMSS.png` 형식으로 저장
- **일시정지(Pause) / 재개(Resume)**
  - 녹화 도중 일시정지 후 다시 이어서 촬영 가능
  - 일시정지 시간은 타임스탬프에서 제외되어 실제 녹화 시간만 표시
  - UI 상에서는 빨간 점 옆의 `|| / ▶` 아이콘으로 상태를 표현
- **미용/색감 필터 (총 11가지)**
  - `Normal`
  - `Pure Pink`
  - `Creamy Latte`
  - `Deep Midnight`
  - `Retro Film`
  - `Daily Natural`
  - `Peach Blossom`
  - `Urban Moody`
  - `Golden Hour`
  - `Classic Noir`
  - `Retro Pixel` (픽셀 아트 / 모자이크)
- **밝기/대비 및 Flip**
  - Contrast(대비)와 Brightness(밝기)를 실시간 조절
  - 좌우 반전(Flip) 토글
- **오버레이 UI**
  - 상단 바: PREVIEW/RECORD 텍스트 + 상단 메뉴(REC, Shot, Flip, Filter, Help, Exit)
  - 하단 도움말: 단축키 안내 (토글 가능)

## 필수 요구사항 매핑

- **현재 카메라 영상 표시**
  - `cv.VideoCapture(0)` 으로 웹캠 프레임을 받아와 메인 윈도우에 출력
- **동영상 파일 저장**
  - `cv.VideoWriter`와 FourCC(`mp4v`)를 이용해 `.mp4` 파일로 저장
- **Preview / Record 모드**
  - `SPACE` 키로 녹화 시작/중지
  - 녹화 중에는 화면 상단에 녹화 인디케이터(빨간 점 + 시간) 표시
- **키보드 조작**
  - `SPACE`: 모드 전환 (Preview ↔ Record)
  - `ESC`: 프로그램 종료

## 추가 구현 기능 상세

- **코덱 및 FPS 사용**
  - `mp4v` 코덱 사용
  - 카메라 FPS를 우선 사용하고, 값이 없으면 기본 30fps로 설정
- **필터 기능**
  - `F` 키로 필터 순환
    - Normal → Pure Pink → Creamy Latte → … → Retro Pixel → Normal …
- **밝기/대비 조절**
  - `+` / `=`: 대비(Contrast) 증가
  - `-` / `_`: 대비(Contrast) 감소
  - `B`: 밝기(Brightness) 증가
  - `N`: 밝기(Brightness) 감소
- **도움말 오버레이**
  - `H` 키로 도움말 표시/숨김 토글
 - **스냅샷 기능**
   - `C` 키 또는 상단 `Shot` 버튼으로 현재 프레임을 이미지로 저장
 - **일시정지 / 재개**
   - `P` 키 또는 빨간 점 옆의 `|| / ▶` 아이콘 클릭으로 일시정지/재개

## 설치 및 실행 방법

1. **패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```

2. **프로그램 실행**

   ```bash
   python video_recorder.py
   ```

   - 기본적으로 `0`번 카메라를 사용합니다.
   - 카메라를 열지 못할 경우, 코드에서 `cv.VideoCapture(0, cv.CAP_DSHOW)`의 첫 번째 인자를 `1`, `2` 등으로 바꾸어 다른 카메라 번호를 시도해볼 수 있습니다.

3. **결과 파일 확인**

   - 녹화가 시작되면, 프로젝트 폴더 내 `recordings/` 디렉터리 아래에 동영상 파일이 생성됩니다.
   - 파일명 예시: record_YYYYMMDD_HHMMSS.mp4 (예: record_20260312_153045.mp4)

## 단축키 정리

- **SPACE**: 녹화 시작/중지 (Preview ↔ Record)
- **ESC**: 프로그램 종료
- **P**: 녹화 일시정지 / 재개
- **C**: 스냅샷(사진) 저장
- **F**: 필터 모드 변경 (11가지 필터 순환)
- **+ / =**: 대비(Contrast) 증가
- **- / _**: 대비(Contrast) 감소
- **B**: 밝기(Brightness) 증가
- **N**: 밝기(Brightness) 감소
- **H**: 도움말 오버레이 토글

## 데모 영상 / 실제 사용 예시

- 데모 영상
  
https://github.com/user-attachments/assets/66256e03-d2aa-4f42-ad1e-9ecaba51bb33

- shot 기능으로 저장한 실제 캡처 이미지 예시
<img width="640" height="480" alt="snapshot_20260317_221317" src="https://github.com/user-attachments/assets/d24bb398-255d-4ec0-9685-f1cdc9b40f67" />


- record 기능으로 저장한 실제 화면 녹화 영상 예시

https://github.com/user-attachments/assets/449e4f6d-a67d-4ad3-b10b-df5bc4cf218f






