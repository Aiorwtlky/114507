#ifndef DROWSINESS_DETECTOR_HPP
#define DROWSINESS_DETECTOR_HPP

#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <string>
#include <vector>
#include <deque>
#include <chrono>

/**
 * 打瞌睡檢測類
 * 負責分析眼睛狀態，檢測駕駛是否打瞌睡
 */
class DrowsinessDetector {
public:
    /**
     * 構造函數
     * @param eye_model_path 眼睛狀態檢測模型路徑 (如果有的話)
     * @param eye_config_path 眼睛狀態檢測配置路徑 (如果有的話)
     * @param eye_aspect_ratio_threshold 眼睛長寬比閾值，低於此值視為閉眼
     * @param consecutive_frames 連續多少幀檢測到閉眼判定為打瞌睡
     */
    DrowsinessDetector(const std::string& eye_model_path = "",
                      const std::string& eye_config_path = "",
                      float eye_aspect_ratio_threshold = 0.2,
                      int consecutive_frames = 30);
    
    /**
     * 初始化打瞌睡檢測器
     * @return 初始化是否成功
     */
    bool initialize();
    
    /**
     * 檢測是否打瞌睡
     * @param frame 原始影像
     * @param face 臉部矩形區域
     * @param eyes 眼睛矩形區域的向量
     * @return 是否檢測到打瞌睡
     */
    bool detectDrowsiness(const cv::Mat& frame, const cv::Rect& face, const std::vector<cv::Rect>& eyes);
    
    /**
     * 計算眼睛長寬比 (Eye Aspect Ratio, EAR)
     * @param eye 眼睛區域
     * @return 眼睛長寬比
     */
    float calculateEAR(const cv::Mat& eye_roi);
    
    /**
     * 獲取當前的睡意等級
     * @return 睡意等級 (0-100)
     */
    int getDrowsinessLevel() const;
    
    /**
     * 在影像上繪製打瞌睡檢測結果
     * @param frame 要繪製的影像
     * @param isDrowsy 是否打瞌睡
     */
    void drawDetectionResult(cv::Mat& frame, bool isDrowsy);

private:
    cv::dnn::Net m_eyeNet;              // 眼睛狀態檢測神經網絡
    std::string m_eyeModelPath;         // 眼睛模型路徑
    std::string m_eyeConfigPath;        // 眼睛配置路徑
    float m_eyeAspectRatioThreshold;    // 眼睛長寬比閾值
    int m_consecutiveFrames;            // 多少連續幀閉眼判定為打瞌睡
    int m_drowsyFrameCount;             // 當前連續閉眼幀數
    bool m_isInitialized;               // 是否已初始化
    int m_drowsinessLevel;              // 睡意等級 (0-100)
    
    // 使用時間窗口來平滑檢測結果
    std::deque<bool> m_recentEyeStates; // 最近的眼睛狀態歷史
    std::chrono::time_point<std::chrono::steady_clock> m_lastWarningTime; // 上次警告時間
    
    /**
     * 更新睡意等級
     * @param isEyeClosed 當前幀眼睛是否閉合
     */
    void updateDrowsinessLevel(bool isEyeClosed);
};

#endif // DROWSINESS_DETECTOR_HPP