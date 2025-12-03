// 檔案路徑: static/js/pages/system_weights.js

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ========== 0. 系統預設值設定 (Factory Defaults) ==========
    // 這些是按下「恢復預設」時會套用的數值
    const DEFAULT_CONFIG = {
        weight: 50,    // 預設車內權重 50%
        interval: 15,  // 預設時間區間 15分鐘
        deductions: {
            'A01': 40, 'A02': 30, 'A03': 15, 'A04': 40,
            'B01': 15, 'B02': 15, 'B03': 15
        }
    };

    // ========== 1. 取得 DOM 元素 ==========
    const slider = document.getElementById('weight-slider');
    const barIn = document.getElementById('bar-in');
    const barOut = document.getElementById('bar-out');
    const sliderVal = document.getElementById('slider-val');
    const formulaIn = document.getElementById('formula-in');
    const formulaOut = document.getElementById('formula-out');
    
    const btnMinus = document.getElementById('btn-minus');
    const btnPlus = document.getElementById('btn-plus');
    const timeDisplay = document.getElementById('time-val');
    
    const simSegments = document.getElementById('sim-segments');
    const simCheckpoints = document.getElementById('sim-checkpoints');
    
    const btnSave = document.getElementById('btn-save');
    const btnReset = document.getElementById('btn-reset'); // [新增] 恢復按鈕
    const roleDisplay = document.getElementById('current-role-display');

    // 取得所有的扣分輸入框
    const deductionInputs = document.querySelectorAll('.std-points-input');

    // ========== 2. 權限檢查邏輯 (Security Check) ==========
    const userProfile = JSON.parse(localStorage.getItem('userProfile'));
    
    // 如果沒有登入或權限不足，踢回 Dashboard
    if (!userProfile || (!userProfile.is_staff && !userProfile.is_group_admin)) {
        alert('權限不足：此頁面僅供管理者使用。');
        window.location.href = "/dashboard";
        return;
    }

    // 顯示管理員身分
    if (userProfile.is_staff) {
        roleDisplay.textContent = "系統管理員";
        roleDisplay.style.borderColor = "#fcd34d";
        roleDisplay.style.backgroundColor = "#fffbeb";
        roleDisplay.style.color = "#d97706";
    } else {
        roleDisplay.textContent = "群組管理員";
    }

    // ========== 3. 狀態管理 (State Management) ==========
    
    // 當前狀態 (初始載入時讀取 HTML 上的 value)
    let currentState = {
        weight: parseInt(slider.value),
        interval: parseInt(timeDisplay.textContent),
        deductions: {}
    };

    // 初始化：讀取所有輸入框的初始值到 currentState
    deductionInputs.forEach(input => {
        const id = input.id.replace('input-', ''); // 例如 A01
        currentState.deductions[id] = parseInt(input.value);
    });

    // 備份一份初始狀態，用於比對是否有變更 (Dirty Check)
    // 注意：這裡假設「載入時的狀態」等於「伺服器上的狀態」
    let savedState = JSON.parse(JSON.stringify(currentState));

    // UI 更新函式
    function updateUI() {
        // --- 更新權重部分 ---
        const val = currentState.weight;
        const decimal = (val / 100).toFixed(2);
        
        barIn.style.width = `${val}%`;
        barIn.textContent = `${val}%`;
        barOut.style.width = `${100 - val}%`;
        barOut.textContent = `${100 - val}%`;
        
        sliderVal.textContent = decimal;
        formulaIn.textContent = decimal;
        formulaOut.textContent = (1 - decimal).toFixed(2);
        slider.value = val;

        // --- 更新時間部分 ---
        timeDisplay.textContent = currentState.interval;
        const segments = Math.ceil(60 / currentState.interval);
        simSegments.textContent = `${segments} 段`;
        simCheckpoints.textContent = `${segments} 次`;

        // --- 更新扣分欄位部分 (針對恢復預設時需要刷新) ---
        deductionInputs.forEach(input => {
            const id = input.id.replace('input-', '');
            // 只有當 DOM 值與 State 值不一致時才更新，避免打字時游標跳掉
            if (parseInt(input.value) !== currentState.deductions[id]) {
                input.value = currentState.deductions[id];
            }
        });

        // --- 檢查是否需要啟用儲存按鈕 ---
        checkDirty();
    }

    // 檢查變更函式 (Dirty Check)
    function checkDirty() {
        let isDirty = false;

        if (currentState.weight !== savedState.weight) isDirty = true;
        if (currentState.interval !== savedState.interval) isDirty = true;

        // 檢查每個扣分項目是否改變
        for (const key in currentState.deductions) {
            if (currentState.deductions[key] !== savedState.deductions[key]) {
                isDirty = true;
                break;
            }
        }

        if (isDirty) {
            btnSave.disabled = false;
            btnSave.style.opacity = '1';
            btnSave.style.cursor = 'pointer';
            btnSave.innerHTML = '<i class="fa-solid fa-save"></i> 儲存設定';
        } else {
            btnSave.disabled = true;
            btnSave.style.opacity = '0.6';
            btnSave.style.cursor = 'not-allowed';
            btnSave.innerHTML = '<i class="fa-solid fa-check"></i> 目前已是最新設定';
        }
    }

    // ========== 4. 事件監聽器 (Event Listeners) ==========

    // 權重滑桿
    slider.addEventListener('input', function(e) {
        currentState.weight = parseInt(e.target.value);
        updateUI();
    });

    // 時間減少
    btnMinus.addEventListener('click', function() {
        if (currentState.interval > 5) {
            currentState.interval -= 5;
            updateUI();
        }
    });

    // 時間增加
    btnPlus.addEventListener('click', function() {
        if (currentState.interval < 60) {
            currentState.interval += 5;
            updateUI();
        }
    });

    // 監聽所有扣分輸入框
    deductionInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const id = e.target.id.replace('input-', '');
            const val = parseInt(e.target.value) || 0; // 若清空則設為 0
            currentState.deductions[id] = val;
            checkDirty();
        });
    });

    // [新增功能] 恢復預設按鈕
    btnReset.addEventListener('click', function() {
        if (confirm('確定要將所有設定（包含權重、時間、各項扣分）恢復為系統預設值嗎？')) {
            // 將 Current State 覆蓋為 Default Config
            currentState = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
            updateUI(); // 刷新畫面
            // 此時 isDirty 會變為 true (因為與 savedState 不同)，Save 按鈕會亮起
        }
    });

    // 儲存按鈕
    btnSave.addEventListener('click', function() {
        // 鎖定按鈕
        btnSave.disabled = true;
        btnSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 儲存中...';

        // 準備要傳給後端的資料
        const payload = {
            in_car_weight: currentState.weight / 100,
            out_car_weight: (100 - currentState.weight) / 100,
            interval_minutes: currentState.interval,
            deductions: currentState.deductions
        };

        console.log("Saving settings to backend:", payload);

        // 模擬 API 呼叫延遲
        setTimeout(() => {
            alert('設定已更新成功！\n系統將立即套用新的權重與扣分標準。');
            
            // 儲存成功，將當前狀態視為已儲存狀態
            savedState = JSON.parse(JSON.stringify(currentState));
            updateUI(); // 重新檢查 Dirty 狀態 (按鈕會變灰)
        }, 800);
    });

    // ========== 5. 初始化頁面 ==========
    updateUI();
});