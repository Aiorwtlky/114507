#ifndef FACE_DETECTOR_HPP
#define FACE_DETECTOR_HPP

#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <string>
#include <vector>

/**
 * 臉部檢測類
 * 負責檢測影像中的臉部，以及臉部特徵點(眼睛、嘴巴等)
 */
class FaceDetector {
public:
    /**
     * 構造函數
     * @param face_model_path 臉部檢測模型路徑
     * @param face_config_path 臉部檢測配置路徑
     * @param confidence_threshold 臉部檢測置信度閾值
     */
    FaceDetector(const std::string& face_model_path = "models/face_detection.caffemodel",
                const std::string& face_config_path = "models/face_detection.prototxt",
                float confidence_threshold = 0.5);
    
    /**
     * 初始化臉部檢測器
     * @return 初始化是否成功
     */
    bool initialize();
    
    /**
     * 檢測影像中的臉部
     * @param frame 輸入影像
     * @return 臉部矩形區域的向量
     */
    std::vector<cv::Rect> detectFaces(const cv::Mat& frame);
    
    /**
     * 檢測臉部中的眼睛
     * @param face_roi 臉部的感興趣區域
     * @return 眼睛矩形區域的向量 [左眼，右眼]
     */
    std::vector<cv::Rect> detectEyes(const cv::Mat& face_roi);
    
    /**
     * 在影像上繪製檢測結果
     * @param frame 要繪製的影像
     * @param faces 臉部矩形區域的向量
     */
    void drawDetections(cv::Mat& frame, const std::vector<cv::Rect>& faces);
    
    /**
     * 在影像上繪製眼睛檢測結果
     * @param face_roi 臉部的感興趣區域
     * @param eyes 眼睛矩形區域的向量
     */
    void drawEyeDetections(cv::Mat& face_roi, const std::vector<cv::Rect>& eyes);

private:
    cv::dnn::Net m_faceNet;           // 臉部檢測神經網絡
    cv::CascadeClassifier m_eyeCascade; // 眼睛級聯分類器
    std::string m_faceModelPath;      // 臉部模型路徑
    std::string m_faceConfigPath;     // 臉部配置路徑
    float m_confidenceThreshold;      // 置信度閾值
    bool m_isInitialized;             // 是否已初始化
};

#endif // FACE_DETECTOR_HPP