"""
推荐功能相关的Schema定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class UserProfileForRecommendation(BaseModel):
    """用户个人资料，用于推荐"""
    user_id: str = Field(..., description="用户ID")
    age: int = Field(..., description="年龄")
    gender: str = Field(..., description="性别")
    height: float = Field(..., description="身高(cm)")
    current_weight: float = Field(..., description="当前体重(kg)")
    target_weight: Optional[float] = Field(None, description="目标体重(kg)")
    initial_weight: Optional[float] = Field(None, description="初始体重(kg)")
    
    @property
    def bmi(self) -> float:
        """计算BMI"""
        height_m = self.height / 100
        return round(self.current_weight / (height_m * height_m), 1)


class CheckInRecordForRecommendation(BaseModel):
    """打卡记录，用于推荐"""
    check_in_date: date = Field(..., description="打卡日期")
    weight: float = Field(..., description="体重(kg)")
    note: Optional[str] = Field(None, description="备注")
    
    @property
    def bmi(self) -> float:
        """计算BMI"""
        return 0.0


class RecommendationRequest(BaseModel):
    """发送给模型侧的请求数据"""
    user_profile: UserProfileForRecommendation = Field(..., description="用户个人资料")
    check_in_records: List[CheckInRecordForRecommendation] = Field(..., description="最近的打卡记录")
    request_type: str = Field(..., description="请求类型：login 或 check_in")


class ExerciseRecommendation(BaseModel):
    """运动推荐"""
    type: str = Field(..., description="运动类型")
    duration: int = Field(..., description="推荐时长(分钟)")
    intensity: str = Field(..., description="强度：low/medium/high")
    description: Optional[str] = Field(None, description="运动说明")


class DietRecommendation(BaseModel):
    """饮食推荐"""
    meal_type: str = Field(..., description="餐次：breakfast/lunch/dinner/snack")
    food_items: List[str] = Field(..., description="推荐食物")
    calories: Optional[int] = Field(None, description="推荐热量(千卡)")
    tips: Optional[str] = Field(None, description="饮食小贴士")


class RecommendationResponse(BaseModel):
    """从模型侧返回的推荐结果"""
    success: bool = Field(..., description="是否成功")
    exercise_recommendations: List[ExerciseRecommendation] = Field(default_factory=list, description="运动推荐列表")
    diet_recommendations: List[DietRecommendation] = Field(default_factory=list, description="饮食推荐列表")
    daily_calories_target: Optional[int] = Field(None, description="每日热量目标")
    water_intake_target: Optional[int] = Field(None, description="每日饮水目标(ml)")
    sleep_target: Optional[int] = Field(None, description="每日睡眠目标(小时)")
    tips: Optional[str] = Field(None, description="综合建议")
    generated_at: datetime = Field(default_factory=datetime.now, description="推荐生成时间")


class CachedRecommendation(BaseModel):
    """缓存的推荐结果"""
    user_id: str = Field(..., description="用户ID")
    recommendation: RecommendationResponse = Field(..., description="推荐结果")
    cached_at: datetime = Field(default_factory=datetime.now, description="缓存时间")
    expires_at: datetime = Field(..., description="过期时间")
