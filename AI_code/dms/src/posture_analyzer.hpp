#ifndef POSTURE_ANALYZER_HPP
#define POSTURE_ANALYZER_HPP

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <deque>

/**
 * 姿態分析類
 * 負責分析駕駛的姿態，檢測是否有危險的駕駛行為
 */
class PostureAnalyzer {
public:
    /**
     * 構造函數
     * @param movement_threshold 運動閾值，超過此值視為大幅度運動
     * @param history_size 歷史幀數用於運動檢測
     */
    PostureAnalyzer(float movement_threshold = 20.0f, int history_size = 10);
    
    /**
     * 初始化姿態分析器
     * @return 初始化是否成功
     */
    bool initialize();
    
    /**
     * 分析駕駛姿態
     * @param frame 當前幀
     * @param face 臉部位置
     * @return 是否檢測到異常駕駛姿態
     */
    bool analyzePosture(const cv::Mat& frame, const cv::Rect& face);
    
    /**
     * 檢測頭部運動
     * @param current_face 當前幀的臉部位置
     * @return 是否檢測到大幅度頭部運動
     */
    bool detectHeadMovement(const cv::Rect& current_face);
    
    /**
     * 在影像上繪製姿態分析結果
     * @param frame 要繪製的影像
     * @param isAbnormal 是否為異常姿態
     */
    void drawAnalysisResult(cv::Mat& frame, bool isAbnormal);
    
    /**
     * 重置分析器狀態
     */
    void reset();

private:
    float m_movementThreshold;    // 運動閾值
    int m_historySize;            // 歷史幀數
    bool m_isInitialized;         // 是否已初始化
    
    std::deque<cv::Rect> m_faceHistory;   // 臉部位置歷史
    std::deque<cv::Point> m_motionHistory; // 運動軌跡歷史
    
    /**
     * 計算兩個矩形之間的距離
     * @param r1 第一個矩形
     * @param r2 第二個矩形
     * @return 兩個矩形中心點之間的歐氏距離
     */
    float calculateRectDistance(const cv::Rect& r1, const cv::Rect& r2);
};

#endif // POSTURE_ANALYZER_HPP