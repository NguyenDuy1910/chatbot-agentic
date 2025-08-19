// Mock data for charts and analytics

export interface ChatTrafficData {
  date: string;
  sessions: number;
  messages: number;
  avgDuration: number;
}

export interface UserActivityData {
  date: string;
  activeUsers: number;
  newRegistrations: number;
  retention: number;
}

export interface APIUsageData {
  date: string;
  apiCalls: number;
  tokens: number;
  cost: number;
  avgResponseTime: number;
}

// Generate mock data for the last 30 days
const generateDateRange = (days: number): string[] => {
  const dates: string[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(date.toISOString().split('T')[0]);
  }
  return dates;
};

const dates = generateDateRange(30);

export const chatTrafficData: ChatTrafficData[] = dates.map((date, index) => {
  const baseValue = 100 + Math.sin(index * 0.2) * 30;
  const randomVariation = Math.random() * 40 - 20;
  const weekendFactor = new Date(date).getDay() === 0 || new Date(date).getDay() === 6 ? 0.7 : 1;
  
  const sessions = Math.max(20, Math.floor((baseValue + randomVariation) * weekendFactor));
  
  return {
    date,
    sessions,
    messages: sessions * (3 + Math.random() * 4), // 3-7 messages per session
    avgDuration: 2 + Math.random() * 8, // 2-10 minutes average duration
  };
});

export const userActivityData: UserActivityData[] = dates.map((date, index) => {
  const baseActive = 200 + Math.sin(index * 0.15) * 50;
  const randomVariation = Math.random() * 60 - 30;
  const weekendFactor = new Date(date).getDay() === 0 || new Date(date).getDay() === 6 ? 0.8 : 1;
  
  const activeUsers = Math.max(50, Math.floor((baseActive + randomVariation) * weekendFactor));
  
  return {
    date,
    activeUsers,
    newRegistrations: Math.floor(Math.random() * 15 + 2), // 2-17 new users per day
    retention: 65 + Math.random() * 25, // 65-90% retention rate
  };
});

export const apiUsageData: APIUsageData[] = dates.map((date, index) => {
  const baseCalls = 500 + Math.sin(index * 0.1) * 150;
  const randomVariation = Math.random() * 200 - 100;
  const weekendFactor = new Date(date).getDay() === 0 || new Date(date).getDay() === 6 ? 0.6 : 1;
  
  const apiCalls = Math.max(100, Math.floor((baseCalls + randomVariation) * weekendFactor));
  const tokensPerCall = 150 + Math.random() * 100; // 150-250 tokens per call
  
  return {
    date,
    apiCalls,
    tokens: Math.floor(apiCalls * tokensPerCall),
    cost: apiCalls * tokensPerCall * 0.00002, // $0.00002 per token
    avgResponseTime: 800 + Math.random() * 400, // 800-1200ms response time
  };
});

// Weekly aggregated data for different view modes
export const getWeeklyData = (data: any[], valueKey: string) => {
  const weeklyData: any[] = [];
  
  for (let i = 0; i < data.length; i += 7) {
    const weekData = data.slice(i, i + 7);
    const weekStart = weekData[0]?.date;
    const weekEnd = weekData[weekData.length - 1]?.date;
    
    if (weekData.length > 0) {
      const avgValue = weekData.reduce((sum, item) => sum + item[valueKey], 0) / weekData.length;
      const totalValue = weekData.reduce((sum, item) => sum + item[valueKey], 0);
      
      weeklyData.push({
        date: `${weekStart} - ${weekEnd}`,
        [valueKey]: Math.floor(avgValue),
        [`total${valueKey.charAt(0).toUpperCase() + valueKey.slice(1)}`]: totalValue,
      });
    }
  }
  
  return weeklyData;
};

// Monthly aggregated data
export const getMonthlyData = (data: any[], valueKey: string) => {
  const monthlyData: { [key: string]: any } = {};
  
  data.forEach(item => {
    const month = item.date.substring(0, 7); // YYYY-MM format
    
    if (!monthlyData[month]) {
      monthlyData[month] = {
        date: month,
        count: 0,
        total: 0,
      };
    }
    
    monthlyData[month].count++;
    monthlyData[month].total += item[valueKey];
  });
  
  return Object.values(monthlyData).map(month => ({
    date: month.date,
    [valueKey]: Math.floor(month.total / month.count),
    [`total${valueKey.charAt(0).toUpperCase() + valueKey.slice(1)}`]: month.total,
  }));
};

// Real-time data simulation
export const generateRealTimeData = () => {
  const now = new Date();
  const currentHour = now.getHours();
  
  return {
    currentSessions: Math.floor(20 + Math.sin(currentHour * 0.5) * 15 + Math.random() * 10),
    activeUsers: Math.floor(50 + Math.sin(currentHour * 0.3) * 30 + Math.random() * 20),
    apiCallsPerMinute: Math.floor(5 + Math.sin(currentHour * 0.4) * 3 + Math.random() * 4),
    avgResponseTime: Math.floor(800 + Math.random() * 400),
  };
};
