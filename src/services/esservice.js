// src/services/esservice.js
import axios from 'axios';

const elasticsearchUrl = '/api'; // 使用代理路径
const esClient = axios.create({
    baseURL: process.env.ES_URL || 'http://localhost:9200', // Elasticsearch 的URL
    timeout: 1000,
    headers: { 'Content-Type': 'application/json' }
  });

export async function search(query, indexName = 'nku_index') {
    try {
        console.log('Sending search request to:', `${elasticsearchUrl}/${indexName}/_search`);
        console.log('Query body:', query);

        const response = await axios.post(`${elasticsearchUrl}/${indexName}/_search`, query);
        console.log('Search response:', response.data);

        return response.data;
    } catch (error) {
        console.error('Error searching Elasticsearch:', error);
        throw error;
    }
}

export const getRecommendations = async (params) => {
    const { history, clicked, count } = params;
  
    try {
      const queryBody = buildRecommendationQuery(history, clicked);
  
      // 执行Elasticsearch查询
      const response = await esClient.post(`_search`, queryBody);
      const hits = response.data.hits.hits;
  
      // 返回最多count个推荐结果
      return hits.slice(0, count).map(hit => ({
        title: hit._source.title,
        link: hit._source.html_filename, // 假设链接在html_filename字段中
        description: hit._source.description || '',
        keywords: hit._source.keywords || [],
        id: hit._id
      }));
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      throw error;
    }
  };
  
  const buildRecommendationQuery = (history, clicked) => {
    const shouldClauses = history.map(term => ({
      match: {
        content: {
          query: term,
          boost: 2.0 // 提升查询历史中的关键词权重
        }
      }
    }));
  
    // 如果用户有点击行为，我们可以降低那些文档的评分
    Object.keys(clicked).forEach(docId => {
      shouldClauses.push({
        term: {
          _id: docId
        },
        boost: -clicked[docId] * 0.5 // 点击次数越多，权重越低
      });
    });
  
    return {
      size: 100, // 搜索更多的文档以确保有足够的推荐
      query: {
        function_score: {
          query: {
            bool: {
              should: shouldClauses,
              minimum_should_match: 1 // 至少匹配一项
            }
          },
          score_mode: "sum",
          boost_mode: "multiply"
        }
      },
      sort: [
        { "_score": { "order": "desc" } },
        { "pr": { "order": "desc" }} // 假设有 pr 字段表示页面排名
      ],
      _source: ["title", "description", "keywords", "html_filename"] // 只获取需要的字段
    };
  };