/**
 * 内容爬虫搜索接口 - 可直接注入到网页的完整脚本
 * 
 * 使用方法：
 * 1. 打开 https://e2738697-sketch.github.io/content-recommendation-system/
 * 2. 按F12打开开发者工具
 * 3. 在Console中粘贴此脚本的全部内容
 * 4. 按回车执行
 * 
 * 或者使用浏览器扩展（如Tampermonkey）自动注入
 */

(function() {
    'use strict';
    
    // ========== 配置 ==========
    // API服务地址（如果5000端口被占用，会自动使用5001）
    let API_BASE_URL = 'http://localhost:5000';
    
    // 尝试检测可用的端口（仅在非GitHub Pages环境下）
    async function detectAPIPort() {
        // 如果是GitHub Pages（HTTPS），无法访问localhost，跳过检测
        if (window.location.protocol === 'https:' && window.location.hostname !== 'localhost') {
            console.log('ℹ️  GitHub Pages环境，跳过localhost检测');
            console.log('💡 提示：请在本地启动API服务后使用');
            return;
        }
        
        const ports = [5001, 5000]; // 优先检测5001
        for (const port of ports) {
            try {
                const response = await fetch(`http://localhost:${port}/api/data/list`, { 
                    method: 'GET',
                    mode: 'cors'
                });
                if (response.ok) {
                    API_BASE_URL = `http://localhost:${port}`;
                    console.log(`✅ 检测到API服务运行在端口 ${port}`);
                    return;
                }
            } catch (e) {
                // 继续尝试下一个端口
            }
        }
        console.warn('⚠️  未检测到API服务，使用默认端口5001');
        console.log('💡 提示：请确保API服务正在运行: python3 crawler_api.py');
    }
    
    // 检测API端口
    detectAPIPort();
    
    // ========== 检查是否已添加 ==========
    const existingContainer = document.getElementById('crawler-search-container');
    if (existingContainer && existingContainer.innerHTML.trim().length > 0) {
        console.log('搜索接口已存在，跳过添加');
        return;
    }
    
    // 如果容器存在但是空的，清空它以便重新添加
    if (existingContainer) {
        existingContainer.innerHTML = '';
    }
    
    // ========== 创建搜索接口 ==========
    function createSearchInterface() {
        // 先检查容器是否存在
        let container = document.getElementById('crawler-search-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'crawler-search-container';
        }
        container.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        `;
        
        container.innerHTML = `
            <h2 style="color: white; margin-bottom: 20px; font-size: 24px;">
                🔍 内容搜索与爬取
            </h2>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 25px;">
                输入关键词和筛选条件，自动爬取小红书数据
            </p>
            
            <form id="crawlSearchForm" style="background: white; padding: 25px; border-radius: 10px;">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #333;">
                        搜索关键词 *
                    </label>
                    <input 
                        type="text" 
                        id="crawlKeyword" 
                        required 
                        placeholder="例如：美妆、穿搭、美食..."
                        style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                    >
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #333;">
                        搜索数量 *
                    </label>
                    <input 
                        type="number" 
                        id="crawlCount" 
                        min="1" 
                        max="100" 
                        value="20" 
                        required 
                        placeholder="1-100"
                        style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                    >
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 12px; font-weight: 500; color: #333;">
                        筛选条件（可选）
                    </label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: #666;">
                                最小点赞数
                            </label>
                            <input 
                                type="number" 
                                id="crawlMinLikes" 
                                min="0" 
                                value="0"
                                style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                            >
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: #666;">
                                最小收藏数
                            </label>
                            <input 
                                type="number" 
                                id="crawlMinCollects" 
                                min="0" 
                                value="0"
                                style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                            >
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: #666;">
                                最小评论数
                            </label>
                            <input 
                                type="number" 
                                id="crawlMinComments" 
                                min="0" 
                                value="0"
                                style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                            >
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: #666;">
                                最小分享数
                            </label>
                            <input 
                                type="number" 
                                id="crawlMinShares" 
                                min="0" 
                                value="0"
                                style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; box-sizing: border-box;"
                            >
                        </div>
                    </div>
                </div>
                
                <button 
                    type="submit" 
                    id="crawlSubmitBtn"
                    style="
                        width: 100%; 
                        padding: 14px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; 
                        border: none; 
                        border-radius: 8px; 
                        font-size: 16px; 
                        font-weight: 500;
                        cursor: pointer;
                        transition: transform 0.2s, box-shadow 0.2s;
                    "
                >
                    🚀 开始爬取
                </button>
            </form>
            
            <div id="crawlStatus" style="margin-top: 20px; display: none;"></div>
            <div id="crawlResults" style="margin-top: 20px; display: none;"></div>
        `;
        
        // 添加到页面
        const targetContainer = document.getElementById('crawler-search-container');
        if (targetContainer) {
            // 如果容器已存在，直接填充内容
            targetContainer.innerHTML = container.innerHTML;
            targetContainer.style.cssText = container.style.cssText;
            // 重新获取表单元素并绑定事件
            const form = document.getElementById('crawlSearchForm');
            if (form) {
                form.addEventListener('submit', handleCrawlSearch);
            }
        } else {
            // 如果容器不存在，创建并插入
            const mainContent = document.querySelector('.container') || document.body;
            const header = document.querySelector('.header');
            if (header && header.nextSibling) {
                mainContent.insertBefore(container, header.nextSibling);
            } else {
                mainContent.insertBefore(container, mainContent.firstChild);
            }
            // 绑定事件
            document.getElementById('crawlSearchForm').addEventListener('submit', handleCrawlSearch);
        }
        
        // 按钮悬停效果
        const btn = document.getElementById('crawlSubmitBtn');
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 5px 20px rgba(102, 126, 234, 0.4)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
        
        console.log('✅ 搜索接口已添加到网页');
    }
    
    // ========== 处理搜索请求 ==========
    async function handleCrawlSearch(event) {
        event.preventDefault();
        
        const keyword = document.getElementById('crawlKeyword').value.trim();
        const count = parseInt(document.getElementById('crawlCount').value);
        const minLikes = parseInt(document.getElementById('crawlMinLikes').value || 0);
        const minCollects = parseInt(document.getElementById('crawlMinCollects').value || 0);
        const minComments = parseInt(document.getElementById('crawlMinComments').value || 0);
        const minShares = parseInt(document.getElementById('crawlMinShares').value || 0);
        
        if (!keyword) {
            alert('请输入搜索关键词');
            return;
        }
        
        const submitBtn = document.getElementById('crawlSubmitBtn');
        const statusDiv = document.getElementById('crawlStatus');
        const resultsDiv = document.getElementById('crawlResults');
        
        // 禁用按钮
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ 爬取中...';
        
        // 显示状态
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = `
            <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; color: #0c5460;">
                ⏳ 正在爬取数据，请稍候...（这可能需要几分钟时间）
                <br><small>关键词: ${keyword} | 数量: ${count}</small>
            </div>
        `;
        resultsDiv.style.display = 'none';
        
        try {
            console.log('发送爬取请求:', { keyword, count, minLikes, minCollects, minComments, minShares });
            
            const response = await fetch(`${API_BASE_URL}/api/crawl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keyword: keyword,
                    count: count,
                    min_likes: minLikes,
                    min_collects: minCollects,
                    min_comments: minComments,
                    min_shares: minShares,
                }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('爬取结果:', result);
            
            if (result.success) {
                // 显示成功消息
                statusDiv.innerHTML = `
                    <div style="background: #d4edda; padding: 15px; border-radius: 8px; color: #155724;">
                        ✅ 成功爬取 ${result.data.count} 条数据！
                        <br>
                        <small>文件已保存到: ${result.data.filepath}</small>
                    </div>
                `;
                
                // 显示结果预览
                displayCrawlResults(result.data.notes);
                
                // 保存数据到网页（如果函数存在）
                if (result.data.notes && result.data.notes.length > 0 && typeof window.saveCrawlDataToPage === 'function') {
                    window.saveCrawlDataToPage(result.data.notes, keyword);
                }
                
                // 刷新数据列表（如果页面有刷新功能）
                if (typeof loadData === 'function') {
                    setTimeout(() => {
                        console.log('刷新数据列表...');
                        loadData();
                    }, 2000);
                }
            } else {
                statusDiv.innerHTML = `
                    <div style="background: #f8d7da; padding: 15px; border-radius: 8px; color: #721c24;">
                        ❌ 爬取失败: ${result.message}
                        <br>
                        <small>请检查API服务是否正常运行</small>
                    </div>
                `;
            }
        } catch (error) {
            console.error('爬取错误:', error);
            statusDiv.innerHTML = `
                <div style="background: #f8d7da; padding: 15px; border-radius: 8px; color: #721c24;">
                    ❌ 请求失败: ${error.message}
                    <br>
                    <small>请确保API服务正在运行: <code>python3 crawler_api.py</code></small>
                    <br>
                    <small>API地址: ${API_BASE_URL}</small>
                </div>
            `;
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 开始爬取';
        }
    }
    
    // ========== 显示爬取结果 ==========
    function displayCrawlResults(notes) {
        const resultsDiv = document.getElementById('crawlResults');
        
        if (!notes || notes.length === 0) {
            resultsDiv.innerHTML = '<p style="color: #666; padding: 20px; text-align: center;">暂无数据</p>';
            resultsDiv.style.display = 'block';
            return;
        }
        
        let html = `
            <div style="background: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h3 style="margin-bottom: 15px; color: #333;">爬取结果预览（前10条）</h3>
                <div style="max-height: 500px; overflow-y: auto;">
        `;
        
        notes.slice(0, 10).forEach((note, index) => {
            const title = note.title || note.desc?.substring(0, 50) || '无标题';
            const desc = note.desc?.substring(0, 150) || '无描述';
            
            html += `
                <div style="
                    padding: 15px; 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    margin-bottom: 10px;
                    border-left: 4px solid #667eea;
                ">
                    <h4 style="margin: 0 0 8px 0; color: #333; font-size: 16px;">
                        ${index + 1}. ${title}${title.length > 50 ? '...' : ''}
                    </h4>
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px; line-height: 1.6;">
                        ${desc}${desc.length > 150 ? '...' : ''}
                    </p>
                    <div style="display: flex; gap: 15px; font-size: 12px; color: #999; flex-wrap: wrap;">
                        <span>👍 ${note.liked_count || 0}</span>
                        <span>💬 ${note.comment_count || 0}</span>
                        <span>⭐ ${note.collected_count || 0}</span>
                        <span>📤 ${note.share_count || 0}</span>
                        ${note.note_url ? `<span><a href="${note.note_url}" target="_blank" style="color: #667eea; text-decoration: none;">🔗 查看原文</a></span>` : ''}
                        ${note.nickname ? `<span>👤 ${note.nickname}</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        if (notes.length > 10) {
            html += `
                <p style="text-align: center; color: #999; margin-top: 10px; padding: 10px;">
                    还有 ${notes.length - 10} 条数据...
                </p>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
    }
    
    // ========== 初始化 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSearchInterface);
    } else {
        createSearchInterface();
    }
    
    console.log('📦 内容爬虫搜索接口脚本已加载');
    console.log(`🔗 API地址: ${API_BASE_URL}`);
    
})();
