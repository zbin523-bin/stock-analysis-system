// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Portfolio Management Class
class PortfolioManager {
    constructor() {
        this.portfolioData = null;
        this.isLoading = false;
        this.lastUpdate = null;
    }

    // 获取持仓数据
    async getPortfolio() {
        try {
            this.isLoading = true;
            this.showLoading(true);
            
            const response = await fetch(`${API_BASE_URL}/portfolio`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.portfolioData = await response.json();
            this.lastUpdate = this.portfolioData.lastUpdate ? new Date(this.portfolioData.lastUpdate) : new Date();
            
            // 更新UI
            this.updateUI();
            this.updateDataStatus();
            this.showNotification('数据加载成功', 'success');
            
            return this.portfolioData;
        } catch (error) {
            console.error('获取持仓数据失败:', error);
            this.showNotification('获取数据失败，请检查网络连接', 'error');
            throw error;
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    // 获取单只股票数据
    async getStockData(market, code) {
        try {
            const response = await fetch(`${API_BASE_URL}/stock/${market}/${code}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('获取股票数据失败:', error);
            throw error;
        }
    }

    // 添加持仓
    async addPosition(positionData) {
        try {
            const response = await fetch(`${API_BASE_URL}/positions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(positionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification('持仓添加成功', 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('添加持仓失败:', error);
            this.showNotification('添加持仓失败', 'error');
            throw error;
        }
    }

    // 更新持仓
    async updatePosition(id, positionData) {
        try {
            const response = await fetch(`${API_BASE_URL}/positions/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(positionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification('持仓更新成功', 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('更新持仓失败:', error);
            this.showNotification('更新持仓失败', 'error');
            throw error;
        }
    }

    // 删除持仓
    async deletePosition(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/positions/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification('持仓删除成功', 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('删除持仓失败:', error);
            this.showNotification('删除持仓失败', 'error');
            throw error;
        }
    }

    // 导入Excel文件
    async importExcel(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE_URL}/import/excel`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification(`成功导入 ${result.imported} 条记录`, 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('导入Excel失败:', error);
            this.showNotification('导入Excel失败', 'error');
            throw error;
        }
    }

    // 获取交易记录
    async getTransactions() {
        try {
            const response = await fetch(`${API_BASE_URL}/transactions`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('获取交易记录失败:', error);
            throw error;
        }
    }

    // 添加交易记录
    async addTransaction(transactionData) {
        try {
            const response = await fetch(`${API_BASE_URL}/transactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(transactionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification('交易记录添加成功', 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('添加交易记录失败:', error);
            this.showNotification('添加交易记录失败', 'error');
            throw error;
        }
    }

    // 获取资金流水
    async getCashFlow() {
        try {
            const response = await fetch(`${API_BASE_URL}/cashflow`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('获取资金流水失败:', error);
            throw error;
        }
    }

    // 添加资金流水
    async addCashFlow(flowData) {
        try {
            const response = await fetch(`${API_BASE_URL}/cashflow`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(flowData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification('资金流水添加成功', 'success');
            
            // 刷新数据
            await this.getPortfolio();
            
            return result;
        } catch (error) {
            console.error('添加资金流水失败:', error);
            this.showNotification('添加资金流水失败', 'error');
            throw error;
        }
    }

    // 获取股票分析建议
    async getAnalysis(code) {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/${code}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('获取分析建议失败:', error);
            throw error;
        }
    }

    // 更新UI
    updateUI() {
        if (!this.portfolioData) return;

        const { summary, positions, marketStats } = this.portfolioData;

        // 更新汇总卡片
        this.updateSummaryCards(summary);

        // 更新持仓表格
        this.updatePositionsTable(positions);

        // 更新市场统计
        this.updateMarketStats(marketStats);

        // 更新资金管理
        this.updateCashManagement();

        // 更新最后更新时间
        this.updateLastUpdateTime();
    }

    // 更新汇总卡片
    updateSummaryCards(summary) {
        // 更新总资产
        const totalAssetsElement = document.querySelector('.text-gray-800');
        if (totalAssetsElement) {
            totalAssetsElement.textContent = `¥${summary.totalAssets.toLocaleString()}`;
        }

        // 更新今日盈亏
        const todayProfitElement = document.querySelector('.profit-positive');
        if (todayProfitElement && summary.totalProfit !== undefined) {
            const profitText = summary.totalProfit >= 0 ? `+¥${summary.totalProfit.toLocaleString()}` : `¥${summary.totalProfit.toLocaleString()}`;
            todayProfitElement.textContent = profitText;
        }

        // 更新持仓市值
        const holdingValueElement = document.querySelectorAll('.text-gray-800')[2];
        if (holdingValueElement) {
            holdingValueElement.textContent = `¥${summary.totalValue.toLocaleString()}`;
        }

        // 更新现金余额
        const cashElement = document.querySelectorAll('.text-gray-800')[3];
        if (cashElement) {
            cashElement.textContent = `¥${summary.cashBalance.toLocaleString()}`;
        }
    }

    // 更新持仓表格
    updatePositionsTable(positions) {
        // 更新A股表格
        const aTableBody = document.querySelector('#astocks-table');
        if (aTableBody) {
            const aStocks = positions.filter(pos => pos.market === 'A股');
            aTableBody.innerHTML = aStocks.map(position => this.createPositionRow(position, 'CNY')).join('');
        }

        // 更新美股表格
        const uTableBody = document.querySelector('#ustocks-table');
        if (uTableBody) {
            const uStocks = positions.filter(pos => pos.market === '美股');
            uTableBody.innerHTML = uStocks.map(position => this.createPositionRow(position, 'USD')).join('');
        }

        // 更新港股表格
        const hTableBody = document.querySelector('#hkstocks-table');
        if (hTableBody) {
            const hStocks = positions.filter(pos => pos.market === '港股');
            hTableBody.innerHTML = hStocks.map(position => this.createPositionRow(position, 'HKD')).join('');
        }

        // 更新基金表格
        const fTableBody = document.querySelector('#funds-table');
        if (fTableBody) {
            const funds = positions.filter(pos => pos.market === '基金');
            fTableBody.innerHTML = funds.map(position => this.createPositionRow(position, 'CNY')).join('');
        }
    }

    // 创建持仓行
    createPositionRow(position, currency = 'CNY') {
        // 检查是否有实时数据
        const hasRealTimeData = position.currentPrice > 0 && position.change !== undefined;
        
        // 如果没有实时数据，显示错误状态
        if (!hasRealTimeData) {
            return `
                <tr class="data-error">
                    <td class="px-4 py-3">
                        <div class="flex items-center">
                            <span class="font-medium text-gray-800">${position.name}</span>
                            <span class="ml-2 px-2 py-1 text-xs bg-red-100 text-red-600 rounded-full">数据获取失败</span>
                        </div>
                    </td>
                    <td class="px-4 py-3 text-gray-500">${position.code}</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                    <td class="px-4 py-3 text-gray-500">--</td>
                </tr>
            `;
        }
        
        const profitClass = position.profit >= 0 ? 'profit-positive' : 'profit-negative';
        const profitPercentText = position.profitRate >= 0 ? `+${position.profitRate.toFixed(2)}%` : `${position.profitRate.toFixed(2)}%`;
        
        // 货币符号
        const currencySymbols = {
            'CNY': '¥',
            'USD': '$',
            'HKD': 'HK$'
        };
        const symbol = currencySymbols[currency] || '¥';
        
        const profitText = position.profit >= 0 ? `+${symbol}${position.profit.toFixed(2)}` : `${symbol}${position.profit.toFixed(2)}`;
        const costPriceText = `${symbol}${position.costPrice.toFixed(2)}`;
        const currentPriceText = `${symbol}${position.currentPrice.toFixed(2)}`;
        
        // 添加实时价格变化显示
        let changeText = '';
        let changePercentText = '';
        if (position.change !== undefined && position.changePercent !== undefined) {
            const changeClass = position.change >= 0 ? 'profit-positive' : 'profit-negative';
            const changeSymbol = position.change >= 0 ? '+' : '';
            changeText = `<span class="${changeClass}">${changeSymbol}${symbol}${position.change.toFixed(2)}</span>`;
            changePercentText = `<span class="${changeClass}">${changeSymbol}${position.changePercent.toFixed(2)}%</span>`;
        }
        
        // 计算持仓占比
        const totalValue = position.quantity * position.currentPrice;
        const portfolioTotalValue = this.portfolioData ? this.portfolioData.summary.totalValue : totalValue;
        const holdingPercentage = portfolioTotalValue > 0 ? ((totalValue / portfolioTotalValue) * 100).toFixed(1) : '0.0';

        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${position.code}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${position.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.industry || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${position.quantity}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${costPriceText}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${currentPriceText}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${changeText || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${changePercentText || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm ${profitClass}">${profitText}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm ${profitClass}">${profitPercentText}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${holdingPercentage}%</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button class="text-blue-600 hover:text-blue-900 mr-2" onclick="portfolioManager.analyzePosition('${position.code}')">分析</button>
                    <button class="text-red-600 hover:text-red-900" onclick="portfolioManager.sellPosition('${position.id}')">卖出</button>
                </td>
            </tr>
        `;
    }

    // 更新市场统计
    updateMarketStats(marketStats) {
        // 更新各市场统计卡片
        this.updateMarketCards(marketStats);
        
        // 更新行业分布图表
        this.updateIndustryCharts();
        
        // 更新市场分布图表
        this.updateMarketDistributionChart();
    }

    // 更新市场统计卡片
    updateMarketCards(marketStats) {
        if (!marketStats) return;
        
        Object.keys(marketStats).forEach(market => {
            const stats = marketStats[market];
            
            // 更新市场卡片数据
            const marketCards = document.querySelectorAll('.bg-white.rounded-xl.p-6');
            marketCards.forEach(card => {
                const title = card.querySelector('h3');
                if (title && title.textContent.includes(market)) {
                    // 更新持仓数量
                    const countElement = card.querySelector('.text-2xl');
                    if (countElement) {
                        countElement.textContent = stats.count;
                    }
                    
                    // 更新市值
                    const valueElement = card.querySelectorAll('.text-gray-600')[1];
                    if (valueElement && stats && stats.totalValue !== undefined) {
                        valueElement.textContent = `¥${stats.totalValue.toLocaleString()}`;
                    }
                    
                    // 更新盈亏
                    const profitElement = card.querySelector('.profit-positive, .profit-negative');
                    if (profitElement && stats && stats.totalProfit !== undefined) {
                        const profitText = stats.totalProfit >= 0 ? `+¥${stats.totalProfit.toLocaleString()}` : `¥${stats.totalProfit.toLocaleString()}`;
                        profitElement.textContent = profitText;
                        profitElement.className = stats.totalProfit >= 0 ? 'profit-positive font-semibold' : 'profit-negative font-semibold';
                    }
                }
            });
        });
    }

    // 更新行业分布图表
    updateIndustryCharts() {
        const positions = this.portfolioData && this.portfolioData.positions;
        if (!positions || !Array.isArray(positions)) return;
        
        // 按市场分组统计行业分布
        const marketIndustries = {};
        
        positions.forEach(position => {
            const market = position.market;
            if (!marketIndustries[market]) {
                marketIndustries[market] = {};
            }
            
            const industry = position.industry;
            const value = position.quantity * position.currentPrice;
            
            if (!marketIndustries[market][industry]) {
                marketIndustries[market][industry] = 0;
            }
            marketIndustries[market][industry] += value;
        });

        // 更新美股行业分布
        this.updateSpecificIndustryChart('usIndustryChart', marketIndustries['美股'] || {});
        
        // 更新A股行业分布
        this.updateSpecificIndustryChart('aIndustryChart', marketIndustries['A股'] || {});
        
        // 更新港股行业分布
        this.updateSpecificIndustryChart('hkIndustryChart', marketIndustries['港股'] || {});
    }

    // 更新特定市场的行业分布图表
    updateSpecificIndustryChart(chartId, industryData) {
        const canvas = document.getElementById(chartId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // 销毁现有图表
        if (canvas.chart) {
            canvas.chart.destroy();
        }

        const labels = Object.keys(industryData);
        const data = Object.values(industryData);
        
        if (labels.length === 0) {
            // 如果没有数据，显示空状态
            ctx.font = '14px Arial';
            ctx.fillStyle = '#999';
            ctx.textAlign = 'center';
            ctx.fillText('暂无数据', canvas.width / 2, canvas.height / 2);
            return;
        }

        // 创建新图表
        canvas.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#FF6384',
                        '#C9CBCF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    // 更新市场分布图表
    updateMarketDistributionChart() {
        const canvas = document.getElementById('marketDistributionChart');
        if (!canvas) return;

        const marketStats = this.portfolioData && this.portfolioData.marketStats;
        if (!marketStats) return;
        
        const labels = Object.keys(marketStats);
        const data = labels.map(market => marketStats[market].totalValue);
        
        const ctx = canvas.getContext('2d');
        
        // 销毁现有图表
        if (canvas.chart) {
            canvas.chart.destroy();
        }

        // 创建新图表
        canvas.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    // 更新资金管理
    updateCashManagement() {
        const cashFlow = this.portfolioData && this.portfolioData.cashFlow;
        const positions = this.portfolioData && this.portfolioData.positions;
        
        // 计算各账户现金余额
        const cashBalances = this.calculateCashBalances();
        
        // 更新账户资金状况
        this.updateCashBalances(cashBalances);
        
        // 更新资金流水历史
        this.updateCashFlowHistory(cashFlow);
    }

    // 计算现金余额
    calculateCashBalances() {
        const cashFlow = this.portfolioData && this.portfolioData.cashFlow;
        const balances = {
            'CNY': 0,
            'USD': 0,
            'HKD': 0
        };
        
        if (cashFlow && Array.isArray(cashFlow)) {
            cashFlow.forEach(flow => {
                if (flow.type === '转入') {
                    balances[flow.currency] += flow.amount;
                } else if (flow.type === '转出') {
                    balances[flow.currency] -= flow.amount;
                }
            });
        }
        
        return balances;
    }

    // 更新现金余额显示
    updateCashBalances(balances) {
        // 更新各账户余额
        const accountElements = document.querySelectorAll('#cash-tab .bg-white.rounded-lg.p-6:first-child .space-y-4');
        if (accountElements.length > 0) {
            const accountsContainer = accountElements[0];
            
            // 清空现有内容
            accountsContainer.innerHTML = '';
            
            // 添加各账户余额
            Object.entries(balances).forEach(([currency, balance]) => {
                const accountName = currency === 'CNY' ? 'A股账户' : 
                                  currency === 'USD' ? '美股账户' : '港股账户';
                const currencySymbol = currency === 'CNY' ? '¥' : 
                                    currency === 'USD' ? '$' : 'HK$';
                
                const accountDiv = document.createElement('div');
                accountDiv.className = 'flex justify-between items-center p-3 bg-blue-50 rounded-lg';
                accountDiv.innerHTML = `
                    <div>
                        <p class="font-medium text-gray-800">${accountName}</p>
                        <p class="text-sm text-gray-500">${currency}</p>
                    </div>
                    <span class="text-xl font-bold text-blue-600">${currencySymbol}${balance.toLocaleString()}</span>
                `;
                accountsContainer.appendChild(accountDiv);
            });
            
            // 计算总现金
            const totalCash = Object.values(balances).reduce((sum, balance) => sum + balance, 0);
            
            // 添加总现金
            const totalDiv = document.createElement('div');
            totalDiv.className = 'flex justify-between items-center p-3 bg-green-50 rounded-lg border-t-2 border-green-200';
            totalDiv.innerHTML = `
                <div>
                    <p class="font-medium text-gray-800">总现金</p>
                    <p class="text-sm text-gray-500">多币种合计</p>
                </div>
                <span class="text-xl font-bold text-green-600">¥${totalCash.toLocaleString()}</span>
            `;
            accountsContainer.appendChild(totalDiv);
        }
    }

    // 更新资金流水历史
    updateCashFlowHistory(cashFlow) {
        if (!cashFlow || !Array.isArray(cashFlow)) return;
        
        const historyContainer = document.querySelector('#cash-tab .bg-white.rounded-lg.p-6:last-child .space-y-3');
        if (historyContainer) {
            // 清空现有内容
            historyContainer.innerHTML = '';
            
            // 按日期排序（最新的在前）
            const sortedCashFlow = [...cashFlow].sort((a, b) => new Date(b.date) - new Date(a.date));
            
            // 显示最近的资金流水
            sortedCashFlow.slice(0, 10).forEach(flow => {
                const currencySymbol = flow.currency === 'CNY' ? '¥' : 
                                    flow.currency === 'USD' ? '$' : 'HK$';
                const amountText = flow.type === '转入' ? 
                    `+${currencySymbol}${flow.amount.toLocaleString()}` : 
                    `-${currencySymbol}${flow.amount.toLocaleString()}`;
                const borderColor = flow.type === '转入' ? 'border-green-500' : 'border-red-500';
                const textColor = flow.type === '转入' ? 'text-green-600' : 'text-red-600';
                
                const flowDiv = document.createElement('div');
                flowDiv.className = `flex justify-between items-center p-3 border-l-4 ${borderColor}`;
                flowDiv.innerHTML = `
                    <div>
                        <p class="font-medium text-gray-800">${flow.description}</p>
                        <p class="text-sm text-gray-500">${flow.date} | ${flow.account} | ${flow.currency}</p>
                    </div>
                    <span class="${textColor} font-bold">${amountText}</span>
                `;
                historyContainer.appendChild(flowDiv);
            });
        }
    }

    // 更新最后更新时间
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('lastUpdate');
        if (lastUpdateElement && this.lastUpdate) {
            lastUpdateElement.textContent = this.lastUpdate.toLocaleString('zh-CN');
        }
    }

    // 更新数据状态显示
    updateDataStatus() {
        const dataStatusElement = document.getElementById('dataStatus');
        if (!dataStatusElement) return;
        
        if (!this.portfolioData || !this.portfolioData.positions) {
            dataStatusElement.innerHTML = `
                <div class="w-2 h-2 bg-red-400 rounded-full"></div>
                <span class="text-xs md:text-sm hidden sm:inline-block">数据加载失败</span>
            `;
            return;
        }
        
        // 检查是否有实时数据
        const positions = this.portfolioData.positions;
        let hasRealTimeData = false;
        let dataErrorCount = 0;
        
        positions.forEach(position => {
            if (position.currentPrice > 0 && position.change !== undefined) {
                hasRealTimeData = true;
            } else {
                dataErrorCount++;
            }
        });
        
        if (dataErrorCount === positions.length) {
            // 所有数据都获取失败
            dataStatusElement.innerHTML = `
                <div class="w-2 h-2 bg-red-400 rounded-full"></div>
                <span class="text-xs md:text-sm hidden sm:inline-block">数据获取失败</span>
            `;
        } else if (dataErrorCount > 0) {
            // 部分数据获取失败
            dataStatusElement.innerHTML = `
                <div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span class="text-xs md:text-sm hidden sm:inline-block">部分数据异常</span>
            `;
        } else {
            // 数据正常
            dataStatusElement.innerHTML = `
                <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                <span class="text-xs md:text-sm hidden sm:inline-block">数据正常</span>
            `;
        }
    }

    // 显示加载状态
    showLoading(show) {
        const button = document.querySelector('button[onclick="refreshData()"]');
        if (button) {
            const icon = button.querySelector('i');
            if (show) {
                icon.classList.add('fa-spin');
                button.disabled = true;
            } else {
                icon.classList.remove('fa-spin');
                button.disabled = false;
            }
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 px-4 py-3 rounded-lg text-white font-medium shadow-lg transform transition-all duration-300 translate-x-full`;
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
        };
        
        notification.classList.add(colors[type] || colors.info);
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // 分析持仓
    async analyzePosition(code) {
        try {
            const analysis = await this.getAnalysis(code);
            this.showNotification(`分析建议: ${analysis.recommendation}`, 'info');
        } catch (error) {
            console.error('分析持仓失败:', error);
        }
    }

    // 卖出持仓
    sellPosition(id) {
        if (confirm('确定要卖出这个持仓吗？')) {
            this.deletePosition(id);
        }
    }

    // 自动刷新数据
    startAutoRefresh(interval = 30000) {
        setInterval(() => {
            if (!this.isLoading) {
                this.getPortfolio().catch(error => {
                    console.error('自动刷新失败:', error);
                });
            }
        }, interval);
    }
}

// 移除全局实例创建，避免重复声明 - 由HTML文件管理初始化

// 添加持仓功能
function showAddPositionModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
            <h3 class="text-lg font-bold mb-4">添加持仓</h3>
            <form id="addPositionForm">
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">股票代码</label>
                    <input type="text" id="stockCode" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">股票名称</label>
                    <input type="text" id="stockName" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">市场</label>
                    <select id="stockMarket" class="w-full border rounded px-3 py-2" required>
                        <option value="A股">A股</option>
                        <option value="美股">美股</option>
                        <option value="港股">港股</option>
                        <option value="基金">基金</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">行业</label>
                    <input type="text" id="stockIndustry" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">持仓数量</label>
                    <input type="number" id="stockQuantity" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">成本价</label>
                    <input type="number" id="stockCostPrice" step="0.01" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="flex justify-end space-x-2">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400">取消</button>
                    <button type="submit" class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">添加</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    
    // 绑定表单提交事件
    document.getElementById('addPositionForm').onsubmit = function(e) {
        e.preventDefault();
        addPosition();
    };
}

// 添加持仓到数据库
async function addPosition() {
    const formData = {
        code: document.getElementById('stockCode').value,
        name: document.getElementById('stockName').value,
        market: document.getElementById('stockMarket').value,
        industry: document.getElementById('stockIndustry').value,
        quantity: parseInt(document.getElementById('stockQuantity').value),
        costPrice: parseFloat(document.getElementById('stockCostPrice').value)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/positions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        portfolioManager.showNotification('持仓添加成功', 'success');
        closeModal();
        portfolioManager.getPortfolio(); // 刷新数据
    } catch (error) {
        console.error('添加持仓失败:', error);
        portfolioManager.showNotification('添加持仓失败', 'error');
    }
}

// 关闭模态框
function closeModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
}

// 刷新数据函数
function refreshData() {
    portfolioManager.getPortfolio();
}

// 显示资金流转模态框
function showCashFlowModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
            <h3 class="text-lg font-bold mb-4">资金流转</h3>
            <form id="cashFlowForm">
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">操作类型</label>
                    <select id="flowType" class="w-full border rounded px-3 py-2" required>
                        <option value="转入">转入</option>
                        <option value="转出">转出</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">账户</label>
                    <select id="flowAccount" class="w-full border rounded px-3 py-2" required>
                        <option value="A股账户">A股账户</option>
                        <option value="美股账户">美股账户</option>
                        <option value="港股账户">港股账户</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">币种</label>
                    <select id="flowCurrency" class="w-full border rounded px-3 py-2" required>
                        <option value="CNY">CNY (人民币)</option>
                        <option value="USD">USD (美元)</option>
                        <option value="HKD">HKD (港币)</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">金额</label>
                    <input type="number" id="flowAmount" step="0.01" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">描述</label>
                    <input type="text" id="flowDescription" class="w-full border rounded px-3 py-2" placeholder="例如：初始资金转入">
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-2">日期</label>
                    <input type="date" id="flowDate" class="w-full border rounded px-3 py-2" required>
                </div>
                <div class="flex justify-end space-x-2">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400">取消</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">确认</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    
    // 设置默认日期为今天
    document.getElementById('flowDate').value = new Date().toISOString().split('T')[0];
    
    // 根据账户自动设置币种
    document.getElementById('flowAccount').addEventListener('change', function() {
        const account = this.value;
        const currencySelect = document.getElementById('flowCurrency');
        if (account === 'A股账户') {
            currencySelect.value = 'CNY';
        } else if (account === '美股账户') {
            currencySelect.value = 'USD';
        } else if (account === '港股账户') {
            currencySelect.value = 'HKD';
        }
    });
    
    // 绑定表单提交事件
    document.getElementById('cashFlowForm').onsubmit = function(e) {
        e.preventDefault();
        addCashFlow();
    };
}

// 添加资金流水
async function addCashFlow() {
    const formData = {
        type: document.getElementById('flowType').value,
        account: document.getElementById('flowAccount').value,
        currency: document.getElementById('flowCurrency').value,
        amount: parseFloat(document.getElementById('flowAmount').value),
        description: document.getElementById('flowDescription').value,
        date: document.getElementById('flowDate').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/cashflow`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        portfolioManager.showNotification('资金流转记录添加成功', 'success');
        closeModal();
        portfolioManager.getPortfolio(); // 刷新数据
    } catch (error) {
        console.error('添加资金流水失败:', error);
        portfolioManager.showNotification('添加资金流水失败', 'error');
    }
}