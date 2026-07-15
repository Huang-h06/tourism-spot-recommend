-- ===== 1. 景点表新增字段：评分和攻略信息 =====
ALTER TABLE spots ADD COLUMN IF NOT EXISTS avg_rating DECIMAL(2,1) DEFAULT 0;
ALTER TABLE spots ADD COLUMN IF NOT EXISTS rating_count INT DEFAULT 0;
ALTER TABLE spots ADD COLUMN IF NOT EXISTS best_season VARCHAR(100) DEFAULT '';
ALTER TABLE spots ADD COLUMN IF NOT EXISTS duration VARCHAR(50) DEFAULT '';
ALTER TABLE spots ADD COLUMN IF NOT EXISTS ticket VARCHAR(100) DEFAULT '';
ALTER TABLE spots ADD COLUMN IF NOT EXISTS open_time VARCHAR(200) DEFAULT '';
ALTER TABLE spots ADD COLUMN IF NOT EXISTS transport TEXT DEFAULT '';

-- ===== 2. 评论表新增字段：评分和点赞 =====
ALTER TABLE comments ADD COLUMN IF NOT EXISTS rating INT DEFAULT 5;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS likes INT DEFAULT 0;

-- ===== 3. 更新12个景点的攻略信息 =====
UPDATE spots SET best_season='春秋季（3-5月、9-11月）', duration='建议半天至一天', ticket='免费（部分景点收费）', open_time='全天开放', transport='地铁1号线龙翔桥站，公交多路可达' WHERE name='西湖';
UPDATE spots SET best_season='春秋季（4-5月、9-10月）', duration='建议半天至一天', ticket='旺季60元，淡季40元', open_time='8:30-17:00（旺季延至17:30）', transport='地铁1号线天安门东/西站' WHERE name='故宫';
UPDATE spots SET best_season='春秋季（4-5月、9-11月）', duration='建议2-3天', ticket='225元（4天通票）', open_time='8:00-18:00', transport='张家界火车站/机场，景区有环保车' WHERE name='张家界';
UPDATE spots SET best_season='四季皆宜（最佳3-5月、10-11月）', duration='建议1-2天', ticket='上岛免费（船票35元）', open_time='全天开放', transport='厦门轮渡码头乘船前往' WHERE name='鼓浪屿';
UPDATE spots SET best_season='四季皆宜（最佳4-10月）', duration='建议2-3天', ticket='古城维护费50元', open_time='全天开放', transport='丽江三义机场/火车站，公交可达' WHERE name='丽江';
UPDATE spots SET best_season='夏季（6-9月最佳）', duration='建议7-15天', ticket='各景点票价不等', open_time='各景区不同', transport='拉萨贡嘎机场/火车站，包车/自驾为主' WHERE name='西藏';
UPDATE spots SET best_season='夏秋季（6-10月最佳）', duration='建议7-15天', ticket='各景点票价不等', open_time='各景区不同', transport='乌鲁木齐地窝堡机场，建议自驾或包车' WHERE name='新疆';
UPDATE spots SET best_season='春秋季（3-5月、9-11月）', duration='建议2-3天', ticket='各景点票价不等', open_time='各景区不同', transport='成都双流/天府机场，地铁公交便利' WHERE name='成都';
UPDATE spots SET best_season='春秋季（3-5月、9-11月）', duration='建议2-3天', ticket='各景点票价不等', open_time='各景区不同', transport='重庆江北机场，轻轨公交便利' WHERE name='重庆';
UPDATE spots SET best_season='夏季（6-9月最佳）', duration='建议2-3天', ticket='各景点票价不等', open_time='各景区不同', transport='青岛流亭机场/火车站，公交便利' WHERE name='青岛';
UPDATE spots SET best_season='春秋季（3-5月、9-11月）', duration='建议2-3天', ticket='各景点票价不等', open_time='各景区不同', transport='上海浦东/虹桥机场，地铁公交便利' WHERE name='上海';
UPDATE spots SET best_season='春秋季（3-5月、9-11月）', duration='建议2-3天', ticket='各景点票价不等', open_time='各景区不同', transport='南京禄口机场/南京南站，地铁公交便利' WHERE name='南京';
