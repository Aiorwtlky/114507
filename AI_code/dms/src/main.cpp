#include <opencv2/opencv.hpp>
#include "camera.hpp"
#include "face_detector.hpp"
#include "drowsiness_detector.hpp"
#include "posture_analyzer.hpp"

int main() {
    // 初始化相機
    Camera cam(0, 640, 480);
    if (!cam.initialize()) {
        return -1;
    }

    // 初始化臉部檢測
    FaceDetector faceDetector(
        "models/face_detection.caffemodel",
        "models/face_detection.prototxt",
        0.7f
    );
    if (!faceDetector.initialize()) {
        return -1;
    }

    // 初始化打瞌睡檢測
    DrowsinessDetector drowsinessDetector(
        "models/eye_state.caffemodel",
        "models/eye_state.prototxt",
        0.2f, // EAR 閾值
        10    // 閉眼連續幀數門檻
    );
    if (!drowsinessDetector.initialize()) {
        return -1;
    }

    // 初始化姿態分析器
    PostureAnalyzer postureAnalyzer(15.0f, 10);
    if (!postureAnalyzer.initialize()) {
        return -1;
    }

    std::cout << "系統啟動完成，開始監控駕駛狀態..." << std::endl;

    while (cam.isOpened()) {
        cv::Mat frame = cam.captureFrame();
        if (frame.empty()) continue;

        // 偵測臉部
        std::vector<cv::Rect> faces = faceDetector.detectFaces(frame);
        faceDetector.drawDetections(frame, faces);

        for (const auto& face : faces) {
            // 擷取臉部 ROI
            cv::Mat faceROI = frame(face);

            // 偵測眼睛
            std::vector<cv::Rect> eyes = faceDetector.detectEyes(faceROI);
            faceDetector.drawEyeDetections(faceROI, eyes);

            // 打瞌睡檢測
            bool isDrowsy = drowsinessDetector.detectDrowsiness(frame, face, eyes);
            drowsinessDetector.drawDetectionResult(frame, isDrowsy);

            // 姿態分析
            bool isAbnormalPosture = postureAnalyzer.analyzePosture(frame, face);
            postureAnalyzer.drawAnalysisResult(frame, isAbnormalPosture);
        }

        // 顯示畫面
        cv::imshow("Driver Monitoring System", frame);

        // 按下 ESC 鍵退出
        if (cv::waitKey(1) == 27) break;
    }

    cam.release();
    cv::destroyAllWindows();
    return 0;
}
