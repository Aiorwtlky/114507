#include "face_detector.hpp"
#include <iostream>

FaceDetector::FaceDetector(const std::string& face_model_path,
                         const std::string& face_config_path,
                         float confidence_threshold)
    : m_faceModelPath(face_model_path),
      m_faceConfigPath(face_config_path),
      m_confidenceThreshold(confidence_threshold),
      m_isInitialized(false) {
}

bool FaceDetector::initialize() {
    try {
        // 載入臉部檢測模型
        try {
            m_faceNet = cv::dnn::readNet(m_faceModelPath, m_faceConfigPath);
            std::cout << "成功載入臉部檢測模型" << std::endl;
        } catch (const cv::Exception& e) {
            // 如果DNN模型載入失敗，使用內置的Haar級聯分類器作為後備
            std::cerr << "無法載入DNN臉部檢測模型: " << e.what() << std::endl;
            std::cerr << "切換到使用Haar級聯分類器" << std::endl;
            
            if (!m_faceNet.empty()) {
                m_faceNet = cv::dnn::Net();
            }
        }
        
        // 載入眼睛檢測的Haar級聯分類器
        if (!m_eyeCascade.load(cv::samples::findFile("haarcascade_eye.xml"))) {
            // 嘗試從OpenCV的默認位置加載
            if (!m_eyeCascade.load("/usr/share/opencv4/haarcascades/haarcascade_eye.xml") && 
                !m_eyeCascade.load("/usr/local/share/opencv4/haarcascades/haarcascade_eye.xml")) {
                std::cerr << "無法載入眼睛級聯分類器" << std::endl;
                // 繼續執行，僅臉部檢測功能可用
            } else {
                std::cout << "成功載入眼睛級聯分類器" << std::endl;
            }
        } else {
            std::cout << "成功載入眼睛級聯分類器" << std::endl;
        }
        
        m_isInitialized = true;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "初始化臉部檢測器失敗: " << e.what() << std::endl;
        return false;
    }
}

std::vector<cv::Rect> FaceDetector::detectFaces(const cv::Mat& frame) {
    std::vector<cv::Rect> faces;
    
    if (!m_isInitialized) {
        std::cerr << "臉部檢測器尚未初始化" << std::endl;
        return faces;
    }
    
    try {
        if (!m_faceNet.empty()) {
            // 使用DNN模型進行臉部檢測
            cv::Mat inputBlob = cv::dnn::blobFromImage(frame, 1.0, 
                                                      cv::Size(300, 300), 
                                                      cv::Scalar(104.0, 177.0, 123.0), 
                                                      false, false);
            m_faceNet.setInput(inputBlob);
            cv::Mat detection = m_faceNet.forward();
            
            cv::Mat detectionMat(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());
            
            for (int i = 0; i < detectionMat.rows; i++) {
                float confidence = detectionMat.at<float>(i, 2);
                
                if (confidence > m_confidenceThreshold) {
                    int x1 = static_cast<int>(detectionMat.at<float>(i, 3) * frame.cols);
                    int y1 = static_cast<int>(detectionMat.at<float>(i, 4) * frame.rows);
                    int x2 = static_cast<int>(detectionMat.at<float>(i, 5) * frame.cols);
                    int y2 = static_cast<int>(detectionMat.at<float>(i, 6) * frame.rows);
                    
                    // 確保檢測框在影像範圍內
                    x1 = std::max(0, std::min(x1, frame.cols - 1));
                    y1 = std::max(0, std::min(y1, frame.rows - 1));
                    x2 = std::max(0, std::min(x2, frame.cols - 1));
                    y2 = std::max(0, std::min(y2, frame.rows - 1));
                    
                    faces.push_back(cv::Rect(x1, y1, x2 - x1, y2 - y1));
                }
            }
        } else {
            // 使用Haar級聯分類器作為後備方案
            cv::CascadeClassifier faceCascade;
            // 嘗試載入OpenCV預設的臉部級聯分類器
            if (faceCascade.load(cv::samples::findFile("haarcascade_frontalface_alt.xml")) || 
                faceCascade.load("/usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml") ||
                faceCascade.load("/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml")) {
                
                cv::Mat gray;
                cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
                cv::equalizeHist(gray, gray);
                
                faceCascade.detectMultiScale(gray, faces, 1.1, 3, 0|cv::CASCADE_SCALE_IMAGE, cv::Size(30, 30));
            } else {
                std::cerr << "無法載入臉部級聯分類器" << std::endl;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "臉部檢測過程中發生錯誤: " << e.what() << std::endl;
    }
    
    return faces;
}

std::vector<cv::Rect> FaceDetector::detectEyes(const cv::Mat& face_roi) {
    std::vector<cv::Rect> eyes;
    
    if (!m_isInitialized || m_eyeCascade.empty()) {
        return eyes;
    }
    
    try {
        cv::Mat gray;
        cv::cvtColor(face_roi, gray, cv::COLOR_BGR2GRAY);
        cv::equalizeHist(gray, gray);
        
        m_eyeCascade.detectMultiScale(gray, eyes, 1.1, 3, 0|cv::CASCADE_SCALE_IMAGE, cv::Size(20, 20));
    } catch (const std::exception& e) {
        std::cerr << "眼睛檢測過程中發生錯誤: " << e.what() << std::endl;
    }
    
    return eyes;
}

void FaceDetector::drawDetections(cv::Mat& frame, const std::vector<cv::Rect>& faces) {
    for (const auto& face : faces) {
        // 繪製臉部矩形框
        cv::rectangle(frame, face, cv::Scalar(0, 255, 0), 2);
        
        // 在臉部上方顯示「已檢測到臉部」
        cv::putText(frame, "Face", 
                   cv::Point(face.x, face.y - 10), 
                   cv::FONT_HERSHEY_SIMPLEX, 0.5, 
                   cv::Scalar(0, 255, 0), 2);
    }
}

void FaceDetector::drawEyeDetections(cv::Mat& face_roi, const std::vector<cv::Rect>& eyes) {
    for (const auto& eye : eyes) {
        cv::Point center(eye.x + eye.width/2, eye.y + eye.height/2);
        int radius = cvRound((eye.width + eye.height)*0.25);
        cv::circle(face_roi, center, radius, cv::Scalar(255, 0, 0), 2);
    }
}