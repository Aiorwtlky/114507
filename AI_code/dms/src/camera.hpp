#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <opencv2/opencv.hpp>
#include <string>

/**
 * 相機模組類
 * 負責處理相機的初始化、讀取和釋放
 */
class Camera {
public:
    /**
     * 構造函數
     * @param device_id 相機的設備ID，對於內置相機通常是0
     * @param width 相機捕獲影像的寬度
     * @param height 相機捕獲影像的高度
     */
    Camera(int device_id = 0, int width = 640, int height = 480);
    
    /**
     * 析構函數
     * 釋放相機資源
     */
    ~Camera();
    
    /**
     * 初始化相機
     * @return 初始化是否成功
     */
    bool initialize();
    
    /**
     * 捕獲一幀影像
     * @return 捕獲的影像
     */
    cv::Mat captureFrame();
    
    /**
     * 檢查相機是否已經打開
     * @return 相機是否已打開
     */
    bool isOpened() const;
    
    /**
     * 釋放相機資源
     */
    void release();

private:
    cv::VideoCapture m_capture;   // OpenCV 相機捕獲對象
    int m_deviceId;               // 相機設備ID
    int m_width;                  // 影像寬度
    int m_height;                 // 影像高度
    bool m_isInitialized;         // 相機是否已初始化
};

#endif // CAMERA_HPP