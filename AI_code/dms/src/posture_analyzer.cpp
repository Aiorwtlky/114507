#include "posture_analyzer.hpp"
#include <iostream>
#include <numeric>
#include <cmath>

PostureAnalyzer::PostureAnalyzer(float movement_threshold, int history_size)
    : m_movementThreshold(movement_threshold),
      m_historySize(history_size),
      m_isInitialized(false) {
}

bool PostureAnalyzer::initialize() {
    try {
        // 清空歷史記錄
        m_faceHistory.clear();
        m_motionHistory.clear();
        
        m_isInitialized = true;
        std::cout << "姿態分析器初始化成功" << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "初始化姿態分析器失敗: " << e.what() << std::endl;
        return false;
    }
}

bool PostureAnalyzer::analyzePosture(const cv::Mat& frame, const cv::Rect& face) {
    if (!m_isInitialized) {
        std::cerr << "姿態分析器尚未初始化" << std::endl;
        return false;
    }
    
    bool isAbnormal = false;
    
    try {
        // 檢測頭部運動
        if (face.width > 0 && face.height > 0) {
            isAbnormal = detectHeadMovement(face);
        }
        
        // 這裡可以添加更多駕駛行為分析
        // 例如：身體姿勢分析、手部位置分析等
        
    } catch (const std::exception& e) {
        std::cerr << "姿態分析過程中發生錯誤: " << e.what() << std::endl;
    }
    
    return isAbnormal;
}

bool PostureAnalyzer::detectHeadMovement(const cv::Rect& current_face) {
    // 保存當前臉部位置到歷史記錄
    m_faceHistory.push_back(current_face);
    
    if (m_faceHistory.size() > m_historySize) {
        m_faceHistory.pop_front();
    }
    
    // 至少需要兩個臉部位置才能檢測運動
    if (m_faceHistory.size() < 2) {
        return false;
    }
    
    // 計算最近兩幀的臉部位置變化
    float current_movement = calculateRectDistance(m_faceHistory.back(), 
                                                 *std::next(m_faceHistory.rbegin()));
    
    // 保存運動軌跡
    cv::Point center = cv::Point(current_face.x + current_face.width / 2,
                                current_face.y + current_face.height / 2);
    m_motionHistory.push_back(center);
    
    if (m_motionHistory.size() > m_historySize) {
        m_motionHistory.pop_front();
    }
    
    // 如果當前運動超過閾值，則認為是大幅度運動
    if (current_movement > m_movementThreshold) {
        // 計算最近幾幀的平均運動量，避免誤報
        std::vector<float> recent_movements;
        auto it = m_faceHistory.begin();
        auto prev = it;
        it++;
        
        for (; it != m_faceHistory.end(); ++it, ++prev) {
            recent_movements.push_back(calculateRectDistance(*it, *prev));
        }
        
        float avg_movement = std::accumulate(recent_movements.begin(), recent_movements.end(), 0.0f) / 
                          recent_movements.size();
        
        // 如果平均運動量也超過閾值，則確認為大幅度運動
        if (avg_movement > m_movementThreshold * 0.7f) {
            return true;
        }
    }
    
    return false;
}

float PostureAnalyzer::calculateRectDistance(const cv::Rect& r1, const cv::Rect& r2) {
    cv::Point center1(r1.x + r1.width / 2, r1.y + r1.height / 2);
    cv::Point center2(r2.x + r2.width / 2, r2.y + r2.height / 2);
    
    return std::sqrt(std::pow(center1.x - center2.x, 2) + std::pow(center1.y - center2.y, 2));
}

void PostureAnalyzer::drawAnalysisResult(cv::Mat& frame, bool isAbnormal) {
    // 繪製運動軌跡
    if (m_motionHistory.size() >= 2) {
        auto it = m_motionHistory.begin();
        auto next = std::next(it);
        
        for (; next != m_motionHistory.end(); ++it, ++next) {
            cv::line(frame, *it, *next, cv::Scalar(0, 255, 0), 2);
        }
    }
    
    // 如果檢測到異常姿態，顯示警告訊息
    if (isAbnormal) {
        cv::putText(frame, "警告: 駕駛姿態異常!", cv::Point(10, 110), cv::FONT_HERSHEY_SIMPLEX, 
                   0.9, cv::Scalar(0, 0, 255), 2);
    }
}