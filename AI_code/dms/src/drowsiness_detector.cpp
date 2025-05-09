#include "drowsiness_detector.hpp"
#include <iostream>

DrowsinessDetector::DrowsinessDetector(const std::string& eye_model_path,
                                     const std::string& eye_config_path,
                                     float eye_aspect_ratio_threshold,
                                     int consecutive_frames)
    : m_eyeModelPath(eye_model_path),
      m_eyeConfigPath(eye_config_path),
      m_eyeAspectRatioThreshold(eye_aspect_ratio_threshold),
      m_consecutiveFrames(consecutive_frames),
      m_drowsyFrameCount(0),
      m_isInitialized(false),
      m_drowsinessLevel(0),
      m_lastWarningTime(std::chrono::steady_clock::now()) {
}

bool DrowsinessDetector::initialize() {
    try {
        // 如果有提供眼睛狀態檢測模型，則載入它
        if (!m_eyeModelPath.empty() && !m_eyeConfigPath.empty()) {
            try {
                m_eyeNet = cv::dnn::readNet(m_eyeModelPath, m_eyeConfigPath);
                std::cout << "成功載入眼睛狀態檢測模型" << std::endl;
            } catch (const cv::Exception& e) {
                std::cerr << "無法載入眼睛狀態檢測模型: " << e.what() << std::endl;
                // 繼續執行，將使用基於幾何的方法
                if (!m_eyeNet.empty()) {
                    m_eyeNet = cv::dnn::Net();
                }
            }
        }
        
        m_isInitialized = true;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "初始化打瞌睡檢測器失敗: " << e.what() << std::endl;
        return false;
    }
}

bool DrowsinessDetector::detectDrowsiness(const cv::Mat& frame, const cv::Rect& face, const std::vector<cv::Rect>& eyes) {
    if (!m_isInitialized) {
        std::cerr << "打瞌睡檢測器尚未初始化" << std::endl;
        return false;
    }
    
    bool isEyeClosed = false;
    
    try {
        // 檢查是否檢測到眼睛
        if (eyes.empty()) {
            // 沒有檢測到眼睛，可能眼睛是閉著的或檢測失敗
            // 如果臉部已被檢測到，但眼睛沒有，那麼可能是眼睛閉著
            if (face.width > 0 && face.height > 0) {
                isEyeClosed = true;
            }
        } else {
            // 計算眼睛的平均EAR值
            float totalEAR = 0.0f;
            int validEyes = 0;
            
            for (const auto& eye : eyes) {
                if (eye.width > 0 && eye.height > 0) {
                    // 確保眼睛區域在臉部範圍內
                    cv::Rect eyeInOriginal(face.x + eye.x, face.y + eye.y, eye.width, eye.height);
                    
                    // 確保不超出原始影像邊界
                    eyeInOriginal = eyeInOriginal & cv::Rect(0, 0, frame.cols, frame.rows);
                    
                    if (eyeInOriginal.width > 0 && eyeInOriginal.height > 0) {
                        cv::Mat eyeROI = frame(eyeInOriginal);
                        float ear = calculateEAR(eyeROI);
                        totalEAR += ear;
                        validEyes++;
                    }
                }
            }
            
            // 計算平均EAR
            if (validEyes > 0) {
                float avgEAR = totalEAR / validEyes;
                
                // 如果平均EAR低於閾值，則判定為閉眼
                isEyeClosed = (avgEAR < m_eyeAspectRatioThreshold);
            }
        }
        
        // 更新睡意等級
        updateDrowsinessLevel(isEyeClosed);
        
        // 如果連續多個幀檢測到閉眼，則判定為打瞌睡
        if (isEyeClosed) {
            m_drowsyFrameCount++;
            if (m_drowsyFrameCount >= m_consecutiveFrames) {
                // 檢查距離上次警告的時間
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - m_lastWarningTime).count();
                
                // 至少間隔3秒再次發出警告
                if (elapsed >= 3) {
                    m_lastWarningTime = now;
                    return true;
                }
            }
        } else {
            // 重置計數器
            m_drowsyFrameCount = std::max(0, m_drowsyFrameCount - 1);
        }
        
    } catch (const std::exception& e) {
        std::cerr << "打瞌睡檢測過程中發生錯誤: " << e.what() << std::endl;
    }
    
    return false;
}

float DrowsinessDetector::calculateEAR(const cv::Mat& eye_roi) {
    // 這是一個簡化的EAR計算方法，實際上需要眼睛的關鍵點
    // 由於我們沒有使用專門的臉部關鍵點檢測，這裡使用灰度和邊緣檢測來近似
    
    try {
        cv::Mat gray;
        cv::cvtColor(eye_roi, gray, cv::COLOR_BGR2GRAY);
        
        // 應用閾值處理來找出瞳孔區域
        cv::Mat thresholded;
        cv::threshold(gray, thresholded, 70, 255, cv::THRESH_BINARY_INV);
        
        // 計算非零像素的比例，作為眼睛開合的指標
        int totalPixels = thresholded.rows * thresholded.cols;
        int nonZeroPixels = cv::countNonZero(thresholded);
        
        if (totalPixels > 0) {
            // 比例越高，表示瞳孔區域越大，眼睛越張開
            float ratio = static_cast<float>(nonZeroPixels) / totalPixels;
            return ratio;
        }
    } catch (const std::exception& e) {
        std::cerr << "計算EAR過程中發生錯誤: " << e.what() << std::endl;
    }
    
    return 0.0f;
}

int DrowsinessDetector::getDrowsinessLevel() const {
    return m_drowsinessLevel;
}

void DrowsinessDetector::updateDrowsinessLevel(bool isEyeClosed) {
    // 將當前眼睛狀態添加到歷史記錄中
    m_recentEyeStates.push_back(isEyeClosed);
    
    // 保持歷史記錄不超過100個樣本
    if (m_recentEyeStates.size() > 100) {
        m_recentEyeStates.pop_front();
    }
    
    // 根據歷史記錄計算睡意等級
    if (!m_recentEyeStates.empty()) {
        int closedCount = 0;
        for (bool state : m_recentEyeStates) {
            if (state) {
                closedCount++;
            }
        }
        
        // 閉眼比例作為睡意等級（0-100）
        m_drowsinessLevel = static_cast<int>(100.0f * closedCount / m_recentEyeStates.size());
    } else {
        m_drowsinessLevel = 0;
    }
}

void DrowsinessDetector::drawDetectionResult(cv::Mat& frame, bool isDrowsy) {
    // 在影像上顯示睡意等級
    std::string levelText = "睡意等級: " + std::to_string(m_drowsinessLevel) + "%";
    cv::putText(frame, levelText, cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 0.7, 
               cv::Scalar(0, 255, 255), 2);
    
    // 如果檢測到打瞌睡，顯示警告訊息
    if (isDrowsy) {
        cv::putText(frame, "警告: 駕駛打瞌睡!", cv::Point(10, 70), cv::FONT_HERSHEY_SIMPLEX, 
                   0.9, cv::Scalar(0, 0, 255), 2);
    }
}