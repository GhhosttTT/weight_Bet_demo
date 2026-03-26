# Bugfix Requirements Document

## Introduction

用户在充值成功后立即创建赌注计划时,系统仍然报告余额不足。具体场景为:用户尝试创建需要200元的赌注计划,系统返回余额不足错误,用户充值200元成功后,立即再次尝试创建计划,系统仍然返回余额不足错误,后端日志显示用户余额仍为0.0元。这个bug导致用户无法在充值后立即使用充值金额,严重影响用户体验和业务流程。

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN 用户充值成功(充值接口返回 {"success":true,"message":"充值成功","amount":200.0}) THEN 系统未更新用户余额,余额仍为充值前的值(0.0元)

1.2 WHEN 用户在充值成功后立即创建赌注计划 THEN 系统仍然检查到余额不足(0.0 < 200.0),返回402错误:"余额不足,需要充值 200.0 元"

1.3 WHEN 充值接口返回成功响应 THEN 系统未将充值金额添加到用户的可用余额中

### Expected Behavior (Correct)

2.1 WHEN 用户充值成功(充值接口返回 {"success":true,"message":"充值成功","amount":200.0}) THEN 系统 SHALL 立即更新用户余额,将充值金额添加到用户的可用余额中

2.2 WHEN 用户在充值成功后立即创建赌注计划 THEN 系统 SHALL 检查到余额充足(200.0 >= 200.0),成功创建计划并冻结相应金额

2.3 WHEN 充值接口返回成功响应 THEN 系统 SHALL 在数据库中持久化更新后的用户余额,确保后续查询能获取到最新余额

2.4 WHEN 充值操作完成 THEN 系统 SHALL 创建一条交易记录,记录充值金额和时间

### Unchanged Behavior (Regression Prevention)

3.1 WHEN 用户余额充足时创建赌注计划 THEN 系统 SHALL CONTINUE TO 成功冻结赌金并创建计划

3.2 WHEN 用户余额不足且未充值时创建赌注计划 THEN 系统 SHALL CONTINUE TO 返回余额不足错误

3.3 WHEN 充值失败(充值接口返回失败响应) THEN 系统 SHALL CONTINUE TO 不更新用户余额

3.4 WHEN 用户查询账户余额 THEN 系统 SHALL CONTINUE TO 返回准确的可用余额和冻结余额

3.5 WHEN 系统执行结算转账操作 THEN 系统 SHALL CONTINUE TO 正确更新用户余额

3.6 WHEN 用户提现操作 THEN 系统 SHALL CONTINUE TO 正确扣减用户可用余额
