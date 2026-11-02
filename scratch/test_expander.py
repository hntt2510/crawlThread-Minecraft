import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.services.discovery.query_expander import query_expander

exp = query_expander.expand_query('giẻ lau')
print('Expansion for "giẻ lau":')
print('  Search queries:', exp.search_queries)
print('  Matched cluster:', exp.matched_cluster_label)
print('  Suggested category:', exp.suggested_category)
print('  Suggested topics:', exp.suggested_topics)

sample_clean_post = 'Dọn nhà chuyển nhà đi đúng hợp đồng, dọn dẹp vệ sinh sạch sẽ thơm tho nhưng chủ trọ soi từng góc...'
sample_dating_post = 'Người yêu cũ chia tay 2 năm tự nhiên nhắn tin dạo này em khỏe không...'

score_clean, reason_clean = query_expander.calculate_relevance(sample_clean_post, exp)
print(f'Clean post -> Score: {score_clean}, Reason: {reason_clean}')

score_dating, reason_dating = query_expander.calculate_relevance(sample_dating_post, exp)
print(f'Dating post -> Score: {score_dating}, Reason: {reason_dating}')

