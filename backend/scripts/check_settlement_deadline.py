#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
结算日检查定时任务

此脚本用于定期检查已到期的计划并触发结算流程。
建议配置为每小时执行一次。

使用示例:
    python scripts/check_settlement_deadline.py
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.services.plan_status_manager import PlanStatusManager
from app.services.settlement_choice_service import SettlementChoiceService
from app.services.settlement_service import SettlementService
from app.logger import get_logger

logger = get_logger()


def check_and_trigger_settlement():
    """
    检查到期计划并触发结算选择流程
    
    流程:
    1. 扫描所有 active 状态且 end_date <= now 的计划
    2. 将计划状态标记为 EXPIRED（如果需要）
    3. 检查是否已有结算记录
    4. 如果没有，则提示用户进入结算选择流程
    """
    db = SessionLocal()
    try:
        logger.info("Starting settlement deadline check...")
        
        # 1. 检查并标记过期计划
        expired_plans = PlanStatusManager.check_expired_plans(db)
        
        if not expired_plans:
            logger.info("No expired plans found.")
            return
        
        logger.info(f"Found {len(expired_plans)} expired plans.")
        
        # 2. 遍历过期计划，检查结算状态
        for plan in expired_plans:
            try:
                # 检查是否已存在结算记录
                settlement = SettlementService.get_settlement_by_plan(db, plan.id)
                
                if settlement:
                    logger.info(f"Plan {plan.id} already settled.")
                    continue
                
                # 检查是否已在进行结算选择流程
                try:
                    from sqlalchemy import func
                    from app.models.settlement_choice import SettlementChoice
                    
                    has_choices = db.query(SettlementChoice).filter(
                        SettlementChoice.plan_id == plan.id
                    ).count() > 0
                    
                    if has_choices:
                        logger.info(f"Plan {plan.id} already has settlement choices.")
                        continue
                except Exception as e:
                    logger.error(f"Error checking settlement choices for plan {plan.id}: {e}")
                    continue
                
                # 3. 计划已到期且未结算，需要触发结算选择流程
                # 注意：实际场景中，这里不需要自动触发，而是由用户在 App 端操作
                # 定时任务只负责检查和记录
                logger.info(
                    f"Plan {plan.id} reached settlement deadline. "
                    f"Creator: {plan.creator_id}, Participant: {plan.participant_id}. "
                    f"Waiting for users to submit settlement choices."
                )
                
            except Exception as e:
                logger.error(f"Error processing plan {plan.id}: {e}")
                continue
        
        logger.info("Settlement deadline check completed.")
        
    except Exception as e:
        logger.error(f"Error in settlement deadline check: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    check_and_trigger_settlement()
