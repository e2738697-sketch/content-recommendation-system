/**
 * 登录管理界面
 * 提供小红书和抖音的登录功能
 */

(function() {
    'use strict';
    
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
    
    // 检查是否已添加登录界面
    if (document.getElementById('login-manager-container')) {
        return;
    }
    
    // 创建登录管理界面
    function createLoginInterface() {
        const container = document.createElement('div');
        container.id = 'login-manager-container';
        container.style.cssText = `
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        `;
        
        container.innerHTML = `
            <h2 style="color: white; margin-bottom: 15px; font-size: 22px;">
                🔐 平台登录管理
            </h2>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 20px; font-size: 14px;">
                登录后可以正常爬取数据。登录状态会保存，下次无需重复登录。
            </p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <!-- 小红书登录 -->
                <div style="background: white; padding: 20px; border-radius: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #333; font-size: 18px;">🎨 小红书</h3>
                        <span id="xhs-status" style="padding: 5px 12px; border-radius: 15px; font-size: 12px; background: #f0f0f0; color: #666;">
                            检查中...
                        </span>
                    </div>
                    <button 
                        id="xhs-login-btn"
                        style="
                            width: 100%; 
                            padding: 12px; 
                            background: linear-gradient(135deg, #ff2442 0%, #ff6b9d 100%);
                            color: white; 
                            border: none; 
                            border-radius: 8px; 
                            font-size: 14px; 
                            font-weight: 500;
                            cursor: pointer;
                            transition: transform 0.2s;
                        "
                        onmouseover="this.style.transform='translateY(-2px)'"
                        onmouseout="this.style.transform='translateY(0)'"
                    >
                        🔑 登录小红书
                    </button>
                    <button 
                        id="xhs-logout-btn"
                        style="
                            width: 100%; 
                            margin-top: 10px;
                            padding: 8px; 
                            background: #f0f0f0;
                            color: #666; 
                            border: none; 
                            border-radius: 8px; 
                            font-size: 12px; 
                            cursor: pointer;
                            display: none;
                        "
                    >
                        退出登录
                    </button>
                </div>
                
                <!-- 抖音登录 -->
                <div style="background: white; padding: 20px; border-radius: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #333; font-size: 18px;">🎵 抖音</h3>
                        <span id="douyin-status" style="padding: 5px 12px; border-radius: 15px; font-size: 12px; background: #f0f0f0; color: #666;">
                            检查中...
                        </span>
                    </div>
                    <button 
                        id="douyin-login-btn"
                        style="
                            width: 100%; 
                            padding: 12px; 
                            background: linear-gradient(135deg, #00f0ff 0%, #0080ff 100%);
                            color: white; 
                            border: none; 
                            border-radius: 8px; 
                            font-size: 14px; 
                            font-weight: 500;
                            cursor: pointer;
                            transition: transform 0.2s;
                        "
                        onmouseover="this.style.transform='translateY(-2px)'"
                        onmouseout="this.style.transform='translateY(0)'"
                    >
                        🔑 登录抖音
                    </button>
                    <button 
                        id="douyin-logout-btn"
                        style="
                            width: 100%; 
                            margin-top: 10px;
                            padding: 8px; 
                            background: #f0f0f0;
                            color: #666; 
                            border: none; 
                            border-radius: 8px; 
                            font-size: 12px; 
                            cursor: pointer;
                            display: none;
                        "
                    >
                        退出登录
                    </button>
                </div>
            </div>
            
            <div id="login-status-message" style="margin-top: 15px; display: none;"></div>
        `;
        
        // 添加到页面（在搜索接口之后）
        const searchContainer = document.getElementById('crawler-search-container');
        if (searchContainer && searchContainer.parentNode) {
            searchContainer.parentNode.insertBefore(container, searchContainer.nextSibling);
        } else {
            document.body.insertBefore(container, document.body.firstChild);
        }
        
        // 绑定事件
        bindLoginEvents();
        
        // 检查登录状态
        checkLoginStatus();
    }
    
    // 检查登录状态
    async function checkLoginStatus() {
        const platforms = ['xhs', 'douyin'];
        
        for (const platform of platforms) {
            try {
                const response = await fetch(`${API_BASE_URL}/api/login/status?platform=${platform}`);
                const result = await response.json();
                
                if (result.success && result.data.logged_in) {
                    updateLoginStatus(platform, true, result.data);
                } else {
                    updateLoginStatus(platform, false);
                }
            } catch (error) {
                console.log(`${platform}登录状态检查失败:`, error);
                updateLoginStatus(platform, false);
            }
        }
    }
    
    // 更新登录状态显示
    function updateLoginStatus(platform, isLoggedIn, loginData = null) {
        const statusEl = document.getElementById(`${platform}-status`);
        const loginBtn = document.getElementById(`${platform}-login-btn`);
        const logoutBtn = document.getElementById(`${platform}-logout-btn`);
        
        if (isLoggedIn) {
            statusEl.textContent = '✅ 已登录';
            statusEl.style.background = '#d4edda';
            statusEl.style.color = '#155724';
            loginBtn.textContent = '✅ 已登录';
            loginBtn.disabled = true;
            loginBtn.style.opacity = '0.6';
            logoutBtn.style.display = 'block';
        } else {
            statusEl.textContent = '❌ 未登录';
            statusEl.style.background = '#f8d7da';
            statusEl.style.color = '#721c24';
            loginBtn.textContent = platform === 'xhs' ? '🔑 登录小红书' : '🔑 登录抖音';
            loginBtn.disabled = false;
            loginBtn.style.opacity = '1';
            logoutBtn.style.display = 'none';
        }
    }
    
    // 绑定登录事件
    function bindLoginEvents() {
        // 小红书登录
        document.getElementById('xhs-login-btn').addEventListener('click', () => {
            startLogin('xhs');
        });
        
        document.getElementById('xhs-logout-btn').addEventListener('click', () => {
            clearLogin('xhs');
        });
        
        // 抖音登录
        document.getElementById('douyin-login-btn').addEventListener('click', () => {
            startLogin('douyin');
        });
        
        document.getElementById('douyin-logout-btn').addEventListener('click', () => {
            clearLogin('douyin');
        });
    }
    
    // 启动登录流程
    async function startLogin(platform) {
        const platformName = platform === 'xhs' ? '小红书' : '抖音';
        const loginUrls = {
            'xhs': 'https://www.xiaohongshu.com/explore',
            'douyin': 'https://www.douyin.com/'
        };
        
        try {
            // 请求登录URL
            const response = await fetch(`${API_BASE_URL}/api/login/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ platform: platform }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 打开登录窗口
                const loginUrl = loginUrls[platform];
                const loginWindow = window.open(
                    loginUrl,
                    `${platformName}登录`,
                    'width=800,height=600,scrollbars=yes,resizable=yes'
                );
                
                // 显示提示信息
                showMessage(`请在弹出窗口中登录${platformName}账号，登录完成后点击"保存登录状态"按钮`, 'info');
                
                // 创建保存按钮（在登录窗口中）
                // 注意：由于跨域限制，我们需要使用其他方式
                // 这里提供一个简化的方案：用户手动复制cookies
                
                // 监听窗口关闭，检查是否登录成功
                const checkInterval = setInterval(() => {
                    if (loginWindow.closed) {
                        clearInterval(checkInterval);
                        // 提示用户保存cookies
                        showSaveCookiesDialog(platform);
                    }
                }, 1000);
                
            } else {
                showMessage(`启动登录失败: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('登录启动失败:', error);
            // 直接打开登录页面
            const loginUrl = loginUrls[platform];
            window.open(loginUrl, `${platformName}登录`, 'width=800,height=600');
            showMessage(`已打开${platformName}登录页面，登录完成后请使用浏览器扩展或手动保存cookies`, 'info');
        }
    }
    
    // 显示保存cookies对话框
    function showSaveCookiesDialog(platform) {
        const platformName = platform === 'xhs' ? '小红书' : '抖音';
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 500px;
            width: 90%;
        `;
        
        dialog.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #333;">保存${platformName}登录状态</h3>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px; line-height: 1.6;">
                登录完成后，请按以下步骤保存登录状态：
            </p>
            <ol style="color: #666; margin-bottom: 20px; padding-left: 20px; font-size: 14px; line-height: 2;">
                <li>在${platformName}页面按F12打开开发者工具</li>
                <li>在Console中执行：<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">document.cookie</code></li>
                <li>复制输出的cookies内容</li>
                <li>粘贴到下方输入框中</li>
            </ol>
            <textarea 
                id="cookies-input" 
                placeholder="粘贴cookies内容..."
                style="width: 100%; min-height: 100px; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 12px; font-family: monospace; box-sizing: border-box; margin-bottom: 15px;"
            ></textarea>
            <div style="display: flex; gap: 10px;">
                <button 
                    id="save-cookies-btn"
                    style="flex: 1; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;"
                >
                    保存登录状态
                </button>
                <button 
                    id="cancel-save-btn"
                    style="flex: 1; padding: 12px; background: #f0f0f0; color: #666; border: none; border-radius: 8px; cursor: pointer;"
                >
                    取消
                </button>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        // 绑定事件
        document.getElementById('save-cookies-btn').addEventListener('click', async () => {
            const cookies = document.getElementById('cookies-input').value.trim();
            if (!cookies) {
                alert('请输入cookies内容');
                return;
            }
            
            // 解析cookies
            const cookiesObj = {};
            cookies.split(';').forEach(cookie => {
                const [key, value] = cookie.trim().split('=');
                if (key && value) {
                    cookiesObj[key] = value;
                }
            });
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/login/save`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        platform: platform,
                        cookies: cookiesObj
                    }),
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`✅ ${platformName}登录状态已保存`, 'success');
                    document.body.removeChild(dialog);
                    checkLoginStatus();
                } else {
                    showMessage(`保存失败: ${result.message}`, 'error');
                }
            } catch (error) {
                showMessage(`保存失败: ${error.message}`, 'error');
            }
        });
        
        document.getElementById('cancel-save-btn').addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
    }
    
    // 清除登录
    async function clearLogin(platform) {
        const platformName = platform === 'xhs' ? '小红书' : '抖音';
        
        if (!confirm(`确定要退出${platformName}登录吗？`)) {
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/login/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ platform: platform }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(`✅ ${platformName}登录状态已清除`, 'success');
                checkLoginStatus();
            } else {
                showMessage(`清除失败: ${result.message}`, 'error');
            }
        } catch (error) {
            showMessage(`清除失败: ${error.message}`, 'error');
        }
    }
    
    // 显示消息
    function showMessage(message, type = 'info') {
        const messageEl = document.getElementById('login-status-message');
        messageEl.style.display = 'block';
        messageEl.style.padding = '15px';
        messageEl.style.borderRadius = '8px';
        messageEl.style.marginTop = '15px';
        
        const colors = {
            'success': { bg: '#d4edda', color: '#155724' },
            'error': { bg: '#f8d7da', color: '#721c24' },
            'info': { bg: '#d1ecf1', color: '#0c5460' }
        };
        
        const style = colors[type] || colors.info;
        messageEl.style.background = style.bg;
        messageEl.style.color = style.color;
        messageEl.textContent = message;
        
        // 3秒后自动隐藏
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    }
    
    // 初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createLoginInterface);
    } else {
        createLoginInterface();
    }
    
    console.log('✅ 登录管理界面已加载');
    
})();
