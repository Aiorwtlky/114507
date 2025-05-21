#include "camera.hpp"
#include <iostream>

Camera::Camera(int device_id, int width, int height)
    : m_deviceId(device_id), m_width(width), m_height(height), m_isInitialized(false) {
}

Camera::~Camera() {
    release();
}

bool Camera::initialize() {
    // 嘗試打開相機
    m_capture.open(m_deviceId);
    
    if (!m_capture.isOpened()) {
        std::cerr << "無法打開相機設備 ID: " << m_deviceId << std::endl;
        return false;
    }
    
    // 設置相機解析度
    m_capture.set(cv::CAP_PROP_FRAME_WIDTH, m_width);
    m_capture.set(cv::CAP_PROP_FRAME_HEIGHT, m_height);
    
    // 檢查是否設置成功
    double actualWidth = m_capture.get(cv::CAP_PROP_FRAME_WIDTH);
    double actualHeight = m_capture.get(cv::CAP_PROP_FRAME_HEIGHT);
    
    std::cout << "相機初始化成功。解析度: " << actualWidth << "x" << actualHeight << std::endl;
    
    m_isInitialized = true;
    return true;
}

cv::Mat Camera::captureFrame() {
    cv::Mat frame;
    
    if (!m_isInitialized) {
        std::cerr << "相機尚未初始化，無法捕獲影像" << std::endl;
        return frame;
    }
    
    // 捕獲一幀影像
    m_capture >> frame;
    
    if (frame.empty()) {
        std::cerr << "捕獲空白影像" << std::endl;
    }
    
    return frame;
}

bool Camera::isOpened() const {
    return m_isInitialized && m_capture.isOpened();
}

void Camera::release() {
    if (m_isInitialized) {
        m_capture.release();
        m_isInitialized = false;
        std::cout << "相機資源已釋放" << std::endl;
    }
}