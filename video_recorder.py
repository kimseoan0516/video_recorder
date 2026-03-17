import cv2 as cv
import os
from datetime import datetime
import time
import numpy as np


WINDOW_NAME = "Video Recorder"
RECORDINGS_DIR = "recordings"
SNAPSHOTS_DIR = "snapshots"
BUTTONS = {}


class RecorderState:
    def __init__(self, cap: cv.VideoCapture):
        self.cap = cap
        self.width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv.CAP_PROP_FPS)
        self.fps = fps if fps and fps > 0 else 30.0

        self.fourcc_code = "mp4v"
        self.writer = None
        self.recording = False
        self.paused = False

        # 필터 / 효과 상태
        # 0: Normal
        # 1: Pure Pink
        # 2: Creamy Latte
        # 3: Deep Midnight
        # 4: Retro Film
        # 5: Daily Natural
        # 6: Peach Blossom
        # 7: Urban Moody
        # 8: Golden Hour
        # 9: Classic Noir
        # 10: Retro Pixel
        self.filter_mode = 0
        self.flip_horizontal = False
        self.contrast = 1.0
        self.brightness = 0.0
        self.show_help = True

        # 타임스탬프 계산용
        self.record_start_time = None
        self.elapsed_before_pause = 0.0

        # 스냅샷 플래시 효과
        self.flash_frames = 0

    @property
    def frame_size(self):
        return self.width, self.height

    @property
    def fourcc(self):
        return cv.VideoWriter_fourcc(*self.fourcc_code)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        os.makedirs(RECORDINGS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(RECORDINGS_DIR, f"record_{timestamp}.mp4")
        self.writer = cv.VideoWriter(
            filename,
            self.fourcc,
            self.fps,
            self.frame_size,
        )
        if not self.writer.isOpened():
            print("동영상 파일을 열 수 없습니다. (VideoWriter 실패)")
            self.writer.release()
            self.writer = None
            return
        print(f"녹화 시작: {filename}")
        self.recording = True
        self.paused = False
        self.record_start_time = time.time()
        self.elapsed_before_pause = 0.0

    def stop_recording(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        if self.recording:
            print("녹화 종료")
        self.recording = False
        self.paused = False
        self.record_start_time = None
        self.elapsed_before_pause = 0.0

    def toggle_pause(self):
        if not self.recording:
            return
        if not self.paused:
            # 일시정지 진입: 지금까지의 경과 시간을 누적
            if self.record_start_time is not None:
                self.elapsed_before_pause += time.time() - self.record_start_time
            self.paused = True
        else:
            # 일시정지 해제: 다시 시작 시각 기록
            self.paused = False
            self.record_start_time = time.time()

    def cleanup(self):
        self.stop_recording()
        if self.cap is not None:
            self.cap.release()
        cv.destroyAllWindows()


def apply_filter_and_effects(frame, state: RecorderState):
    processed = cv.convertScaleAbs(frame, alpha=state.contrast, beta=state.brightness)

    if state.flip_horizontal:
        processed = cv.flip(processed, 1)

    if state.filter_mode == 1:
        smooth = cv.bilateralFilter(processed, d=9, sigmaColor=75, sigmaSpace=75)
        blended = cv.addWeighted(processed, 0.5, smooth, 0.5, 0)

        blended = cv.add(blended, 15)
        blended = cv.addWeighted(blended, 0.95, np.full_like(blended, 128), 0.05, 0)

        b, g, r = cv.split(blended)
        r = cv.add(r, 10)
        g = cv.add(g, 5)
        merged = cv.merge((b, g, r))
        processed = np.clip(merged, 0, 255).astype(np.uint8)

    elif state.filter_mode == 2:
        smooth = cv.bilateralFilter(processed, d=7, sigmaColor=60, sigmaSpace=60)
        blended = cv.addWeighted(processed, 0.4, smooth, 0.6, 0)

        hsv = cv.cvtColor(blended, cv.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv.split(hsv)
        s *= 0.9
        v_gamma = (v / 255.0) ** (1 / 1.2) * 255.0
        s = np.clip(s, 0, 255)
        v = np.clip(v_gamma, 0, 255)
        hsv_merged = cv.merge((h, s, v)).astype(np.uint8)
        creamy = cv.cvtColor(hsv_merged, cv.COLOR_HSV2BGR)

        b, g, r = cv.split(creamy)
        r = cv.add(r, 5)
        b = cv.subtract(b, 10)
        merged = cv.merge((b, g, r))
        processed = np.clip(merged, 0, 255).astype(np.uint8)

    elif state.filter_mode == 3:
        hsv = cv.cvtColor(processed, cv.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv.split(hsv)

        s *= 0.8
        shadow_mask = v < 120
        v[shadow_mask] = np.clip(v[shadow_mask] * 0.9, 0, 255)

        hsv = cv.merge((h, s, v)).astype(np.uint8)
        toned = cv.cvtColor(hsv, cv.COLOR_HSV2BGR).astype(np.int16)

        b, g, r = cv.split(toned)
        b = b + 5
        g = g - 5
        merged = cv.merge((b, g, r))
        merged = np.clip(merged, 0, 255).astype(np.uint8)

        processed = cv.addWeighted(merged, 1.15, np.full_like(merged, 128), -0.15, 0)

    elif state.filter_mode == 4:
        lab = cv.cvtColor(processed, cv.COLOR_BGR2LAB).astype(np.float32)
        l, a, b = cv.split(lab)
        l *= 0.9
        a -= 3
        b += 5
        lab = cv.merge((l, a, b))
        retro = cv.cvtColor(lab.astype(np.uint8), cv.COLOR_LAB2BGR)
        processed = np.clip(retro, 0, 255).astype(np.uint8)

    elif state.filter_mode == 5:
        natural = cv.convertScaleAbs(processed, alpha=1.1, beta=5)
        hsv = cv.cvtColor(natural, cv.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv.split(hsv)
        s *= 1.1
        s = np.clip(s, 0, 255)
        hsv = cv.merge((h, s, v)).astype(np.uint8)
        natural = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]], dtype=np.float32)
        sharpened = cv.filter2D(natural, -1, kernel)
        processed = np.clip(sharpened, 0, 255).astype(np.uint8)

    elif state.filter_mode == 6:
        smooth = cv.bilateralFilter(processed, d=9, sigmaColor=80, sigmaSpace=80)
        blended = cv.addWeighted(processed, 0.65, smooth, 0.35, 0)
        blended = cv.add(blended, 10)
        b, g, r = cv.split(blended)
        r = cv.add(r, 15)
        b = cv.add(b, 8)
        merged = cv.merge((b, g, r))
        processed = np.clip(merged, 0, 255).astype(np.uint8)

    elif state.filter_mode == 7:
        hsv = cv.cvtColor(processed, cv.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv.split(hsv)
        s *= 0.8
        s = np.clip(s, 0, 255)
        v_gamma = (v / 255.0) ** 0.9 * 255.0
        v = np.clip(v_gamma, 0, 255)
        hsv = cv.merge((h, s, v)).astype(np.uint8)
        moody = cv.cvtColor(hsv, cv.COLOR_HSV2BGR).astype(np.int16)
        b, g, r = cv.split(moody)
        b = b + 5
        g = g - 5
        merged = cv.merge((b, g, r))
        merged = np.clip(merged, 0, 255).astype(np.uint8)
        processed = cv.addWeighted(merged, 1.15, np.full_like(merged, 128), -0.15, 0)

    elif state.filter_mode == 8:
        warm = processed.astype(np.int16)
        b, g, r = cv.split(warm)
        r = r + 12
        g = g + 8
        b = b - 10
        merged = cv.merge((b, g, r))
        merged = np.clip(merged, 0, 255).astype(np.uint8)
        overlay_color = np.full_like(merged, (20, 80, 160))
        processed = cv.addWeighted(merged, 0.9, overlay_color, 0.1, 0)

    elif state.filter_mode == 9:
        gray = cv.cvtColor(processed, cv.COLOR_BGR2GRAY)
        noir = cv.convertScaleAbs(gray, alpha=1.3, beta=-5)
        noise = np.random.normal(0, 5, noir.shape).astype(np.int16)
        noir = np.clip(noir.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        processed = cv.cvtColor(noir, cv.COLOR_GRAY2BGR)

    elif state.filter_mode == 10:
        h, w = processed.shape[:2]
        scale = 0.15
        small_w = max(16, int(w * scale))
        small_h = max(16, int(h * scale))
        small = cv.resize(processed, (small_w, small_h), interpolation=cv.INTER_LINEAR)
        pixel = cv.resize(small, (w, h), interpolation=cv.INTER_NEAREST)
        processed = pixel

    return processed


def save_snapshot(frame, state: RecorderState):
    """현재 화면을 이미지 파일로 저장 (프리뷰/녹화 여부와 상관없이 사용)."""
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SNAPSHOTS_DIR, f"snapshot_{timestamp}.png")
    # frame은 이미 필터와 flip, 밝기/대비가 적용된 상태라고 가정
    success = cv.imwrite(filename, frame)
    if success:
        print(f"스냅샷 저장: {filename}")
    else:
        print("스냅샷 저장에 실패했습니다.")


def draw_ui(frame, state: RecorderState):
    h, w = frame.shape[:2]

    # 스냅샷 플래시 효과: 몇 프레임 동안 화면을 살짝 하얗게
    if state.flash_frames > 0:
        flash_overlay = np.full_like(frame, 255)
        frame = cv.addWeighted(frame, 0.6, flash_overlay, 0.4, 0)
        state.flash_frames -= 1

    # 버튼 영역 초기화
    BUTTONS.clear()

    # 상단 왼쪽 상태 텍스트 (심플 파스텔톤, 고정 폭 버튼 레이아웃)
    # 사랑스러운 파스텔 핑크 톤 (#ffc1cc = RGB(255,193,204))
    if state.recording:
        mode_text = "RECORDING"
        # 녹화 중: 같은 색을 살짝 더 진하게
        main_color = (190, 180, 255)  # BGR 근사
    else:
        mode_text = "PREVIEW"
        # 기본 PREVIEW: #ffc1cc 에 가까운 톤 (BGR 근사: (204,193,255))
        main_color = (204, 193, 255)

    font_scale = 1.0
    thickness = 2
    text_size, _ = cv.getTextSize(mode_text, cv.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    base_pos = (20, 48)
    # 얇은 회색 그림자 한 번만
    cv.putText(frame, mode_text, (base_pos[0] + 1, base_pos[1] + 1),
               cv.FONT_HERSHEY_SIMPLEX, font_scale, (40, 40, 40), thickness, cv.LINE_AA)
    cv.putText(frame, mode_text, base_pos,
               cv.FONT_HERSHEY_SIMPLEX, font_scale, main_color, thickness, cv.LINE_AA)

    # 버튼들은 항상 고정 위치에서 시작 (PREVIEW/RECORDING 길이와 무관하게)
    # REC/STOP 텍스트가 카메라 아이콘과 겹치지 않도록 약간 더 오른쪽에서 시작
    btn_h = 32
    padding = 14
    x = 220
    y = 24

    def draw_button(name, label, x, y, active=False, accent=False):
        # 텍스트 컬러로만 상태 표현 (#ffc1cc 계열)
        base_color = (245, 238, 245)
        accent_color = (204, 193, 255)   # PREVIEW 톤과 맞춘 파스텔 핑크
        if accent or active:
            color = accent_color
        else:
            color = base_color

        font_scale = 0.7
        thickness = 2 if (active or accent) else 1
        (tw, th), _ = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        baseline = y + btn_h // 2 + th // 2

        cv.putText(
            frame,
            label,
            (x, baseline),
            cv.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv.LINE_AA,
        )

        # 마우스 클릭 영역 저장 (텍스트 주변만)
        BUTTONS[name] = (x, y, x + tw, y + btn_h)
        return x + tw + padding

    # Record / Stop 텍스트 버튼 (왼쪽에 카메라 아이콘 배치)
    rec_label = "STOP" if state.recording else "REC"

    # 카메라 아이콘 (사각형+동그라미 렌즈, PREVIEW와 같은 #ffc1cc 톤)
    cam_w, cam_h = 18, 12
    cam_x1 = x
    cam_y1 = y + (btn_h - cam_h) // 2
    cam_x2 = cam_x1 + cam_w
    cam_y2 = cam_y1 + cam_h
    cv.rectangle(frame, (cam_x1, cam_y1), (cam_x2, cam_y2), (204, 193, 255), thickness=2)
    center = (cam_x1 + cam_w // 2, cam_y1 + cam_h // 2)
    cv.circle(frame, center, 3, (204, 193, 255), thickness=2)

    x = cam_x2 + 8
    x = draw_button("record", rec_label, x, y, active=state.recording and not state.paused, accent=True)

    # Snapshot 텍스트 버튼 (사진 캡처)
    x = draw_button("snapshot", "Shot", x + 10, y)

    # Flip 텍스트 버튼 (텍스트는 항상 'Flip', 활성 시 색/굵기만 변경)
    flip_label = "Flip"
    x = draw_button("flip", flip_label, x, y, active=state.flip_horizontal)

    # Filter 텍스트 버튼
    x = draw_button("filter", "Filter", x, y)

    # Help 텍스트 버튼
    x = draw_button("help", "Help", x, y, active=state.show_help)

    # Exit 텍스트 버튼
    draw_button("exit", "Exit", x, y)

    # 녹화 중일 때: 상단 핑크 바보다 살짝 아래, 좌측 상단에 동그라미/일시정지 아이콘/시간 표시
    if state.recording:
        # 상단 바 높이가 70이므로 그보다 아래쪽에 배치
        rec_center = (40, 90)
        cv.circle(frame, rec_center, 10, (0, 0, 255), thickness=-1)

        # 일시정지 아이콘 (||) - 빨간 동그라미 오른쪽, 수평 정렬
        pause_x1 = rec_center[0] + 22  # 동그라미와의 간격 조금 넓게
        pause_y1 = rec_center[1] - 8
        bar_width = 3
        bar_gap = 4
        bar_height = 16
        # 왼쪽 막대
        cv.rectangle(
            frame,
            (pause_x1, pause_y1),
            (pause_x1 + bar_width, pause_y1 + bar_height),
            (255, 255, 255),
            thickness=-1,
        )
        # 오른쪽 막대
        cv.rectangle(
            frame,
            (pause_x1 + bar_width + bar_gap, pause_y1),
            (pause_x1 + 2 * bar_width + bar_gap, pause_y1 + bar_height),
            (255, 255, 255),
            thickness=-1,
        )

        # 일시정지 아이콘 클릭 영역 등록
        BUTTONS["pause_icon"] = (
            pause_x1,
            pause_y1,
            pause_x1 + 2 * bar_width + bar_gap,
            pause_y1 + bar_height,
        )

        # 녹화 경과 시간 계산 (일시정지 구간 제외)
        elapsed = state.elapsed_before_pause
        if not state.paused and state.record_start_time is not None:
            elapsed += time.time() - state.record_start_time
        elapsed = max(0, int(elapsed))
        minutes = elapsed // 60
        seconds = elapsed % 60
        ts_text = f"{minutes:02d}:{seconds:02d}"
        # 시간 텍스트는 아이콘과 수평 위치에 충분한 간격 두고 배치
        ts_x = pause_x1 + 2 * bar_width + bar_gap + 20
        ts_y = rec_center[1] + 5
        cv.putText(
            frame,
            ts_text,
            (ts_x, ts_y),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv.LINE_AA,
        )

    # 필터 / 효과 상태 표시 및 도움말 (Help ON일 때만, 배경 없이 텍스트만)
    if state.show_help:
        filter_names = {
            0: "Normal",
            1: "Pure Pink",
            2: "Creamy Latte",
            3: "Deep Midnight",
            4: "Retro Film",
            5: "Daily Natural",
            6: "Peach Blossom",
            7: "Urban Moody",
            8: "Golden Hour",
            9: "Classic Noir",
            10: "Retro Pixel",
        }
        filter_text = f"Filter: {filter_names.get(state.filter_mode, 'Unknown')}"
        effect_text = f"Contrast: {state.contrast:.1f}   Brightness: {state.brightness:.0f}"

        # 화면 하단에서 조금 더 여유 있게 위쪽에 표시
        base_y = h - 90

        cv.putText(
            frame,
            filter_text,
            (20, base_y),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv.LINE_AA,
        )
        cv.putText(
            frame,
            effect_text,
            (20, base_y + 24),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv.LINE_AA,
        )

        # 키 도움말 (그 아래쪽에 간단하게 정리해서 배치)
        help_lines = [
            "SPACE: Record / Stop    P: Pause/Resume    ESC: Exit",
            "C: Snapshot    F: Filter cycle    Flip: Button   +/-: Contrast   B/N: Brightness",
        ]
        for i, text in enumerate(help_lines):
            cv.putText(
                frame,
                text,
                (20, base_y + 50 + i * 22),
                cv.FONT_HERSHEY_SIMPLEX,
                0.45,
                (200, 200, 200),
                1,
                cv.LINE_AA,
            )

    return frame


def handle_key(key, state: RecorderState):
    if key == 32:  # SPACE - 녹화 토글
        state.toggle_recording()
    elif key == 27:  # ESC - 종료
        return False
    elif key in (ord("p"), ord("P")):
        state.toggle_pause()
    elif key in (ord("c"), ord("C")):
        # 'C' 키로 스냅샷 촬영 (실제 저장은 메인 루프에서 현재 프레임으로 처리)
        state._request_snapshot = True
    elif key in (ord("f"), ord("F")):
        # 필터 모드 0~10 순환
        state.filter_mode = (state.filter_mode + 1) % 11
    elif key == ord("+") or key == ord("="):
        state.contrast = min(3.0, state.contrast + 0.1)
    elif key == ord("-") or key == ord("_"):
        state.contrast = max(0.2, state.contrast - 0.1)
    elif key in (ord("b"), ord("B")):
        state.brightness = min(100.0, state.brightness + 5.0)
    elif key in (ord("n"), ord("N")):
        state.brightness = max(-100.0, state.brightness - 5.0)
    elif key in (ord("h"), ord("H")):
        state.show_help = not state.show_help
    return True


def handle_click(event, x, y, flags, userdata):
    state: RecorderState = userdata
    if event != cv.EVENT_LBUTTONDOWN:
        return

    for name, (x1, y1, x2, y2) in BUTTONS.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            if name == "record":
                state.toggle_recording()
            elif name in ("pause", "pause_icon"):
                state.toggle_pause()
            elif name == "snapshot":
                # 현재 프레임에 대해 스냅샷 요청 (실제 저장은 메인 루프에서 처리)
                state._request_snapshot = True
            elif name == "flip":
                state.flip_horizontal = not state.flip_horizontal
            elif name == "filter":
                state.filter_mode = (state.filter_mode + 1) % 11
            elif name == "help":
                state.show_help = not state.show_help
            elif name == "exit":
                # exit 요청을 ESC와 동일하게 처리하기 위해 특별 플래그 사용
                state._request_exit = True  # 동적으로 속성 추가
            break


def main():
    # 0번 카메라 오픈
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다. 다른 번호를 시도해 보세요.")
        return

    state = RecorderState(cap)
    cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
    cv.resizeWindow(WINDOW_NAME, state.width, state.height)
    cv.setMouseCallback(WINDOW_NAME, handle_click, state)

    # 마우스 종료 / 스냅샷 요청 플래그 초기화
    state._request_exit = False
    state._request_snapshot = False

    print("Video Recorder 실행")
    print("SPACE: 녹화 시작/중지, ESC: 종료, F: 필터 변경, +/-: 대비, B/N: 밝기, H: 도움말 토글")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다. 종료합니다.")
                break

            processed = apply_filter_and_effects(frame, state)

            if state.recording and not state.paused and state.writer is not None:
                state.writer.write(processed)

            # 스냅샷 요청이 있으면, UI 오버레이를 그리기 전에 순수 영상 기준으로 저장
            if getattr(state, "_request_snapshot", False):
                save_snapshot(processed, state)
                state._request_snapshot = False
                # 화면 플래시 효과를 위해 몇 프레임 동안 밝게 처리
                state.flash_frames = 3

            ui_frame = draw_ui(processed, state)
            cv.imshow(WINDOW_NAME, ui_frame)

            key = cv.waitKey(1) & 0xFF
            if key != 255:
                if not handle_key(key, state):
                    break

            # 마우스로 Exit 버튼 눌렀는지 확인
            if getattr(state, "_request_exit", False):
                break
    finally:
        state.cleanup()


if __name__ == "__main__":
    main()

