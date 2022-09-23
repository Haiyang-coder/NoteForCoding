#DFA算法实现敏感词的过滤
##1.算法用到的数据结构
![图示数据结构](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/dd.png)
>如图所示
>1. 森林:敏感词库
>2. 树:都是开头字符相同的敏感词汇
>3. 节点:节点需要包含连个信息
> 1.单个敏感字符
> 2.是否是敏感词的结尾


##2.算法的java代码实现
代码中采用了hashmap的数据结构,key和vlues 都是obj类型有以下几种搭配
>"endl" = "1"
>"操" = {}(这里的{}里面存放的是HashMap()结构)
如此的循环套娃就成了
```java
package com.shk.utils;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

/**
 * @author: sunhengkang
 * @date:2022/9/22
 */
public class SensitivewordFilter {
    //敏感词树
    private static HashMap sensitiveWordMap = null;
    //匹配规则
    public static final int MinMatchTYpe = 1;      //最小匹配规则，如：敏感词库["中国","中国人"]，语句："我是中国人"，匹配结果：我是[中国]人
    public static final int MaxMatchType = 2;      //最大匹配规则，如：敏感词库["中国","中国人"]，语句："我是中国人"，匹配结果：我是[中国人]

    /**
     * 初始化敏感词库，构建DFA算法模型
     *
     * @param sensitiveWordSet 敏感词库
     */
    public static synchronized void init(Set<String> sensitiveWordSet) {
        addSensitiveWordToHashMap(sensitiveWordSet);
    }
        /**
         * 初始化数据库中的敏感词，将数据库中的敏感次构建成
         * 数，树状结构便于之后查找，注意采用了hashmap来存储
         * @param keyWordSet 敏感词字符串合集
         */
    @SuppressWarnings({ "rawtypes", "unchecked" })
    private static void addSensitiveWordToHashMap(Set<String> keyWordSet) {
        sensitiveWordMap = new HashMap(keyWordSet.size());//初始化敏感词容器
        String key = null;
        Map nowMap = null;
        Map<String, String> newWorMap = null;
        //迭代keyWordSet
        Iterator<String> iterator = keyWordSet.iterator();
        while (iterator.hasNext()) {
            key = iterator.next();    //关键字
            nowMap = sensitiveWordMap;
            for (int i = 0; i < key.length(); i++) {
                char keyChar = key.charAt(i);       //转换成char型
                Object wordMap = nowMap.get(keyChar);       //获取

                if (wordMap != null) {        //如果存在该key，直接赋值
                    nowMap = (Map) wordMap;
                } else {     //不存在则，则构建一个map，同时将isEnd设置为0，因为他不是最后一个
                    newWorMap = new HashMap<String, String>();
                    newWorMap.put("isEnd", "0");
                    nowMap.put(keyChar, newWorMap);
                    nowMap = newWorMap;
                }

                if (i == key.length() - 1) {
                    nowMap.put("isEnd", "1");    //最后一个                }
                }
            }
        }
    }

    @SuppressWarnings({ "rawtypes"})
    private static int checkSensitiveWord(String txt,int beginIndex,int matchType){
        boolean  flag = false;    //敏感词结束标识位：用于敏感词只有1位的情况
        int matchFlag = 0;     //匹配标识数默认为0
        char word = 0;
        Map nowMap = sensitiveWordMap;
        for(int i = beginIndex; i < txt.length() ; i++){
            word = txt.charAt(i);
            nowMap = (Map) nowMap.get(word);     //获取指定key
            if(nowMap != null){     //存在，则判断是否为最后一个
                matchFlag++;     //找到相应key，匹配标识+1
                if("1".equals(nowMap.get("isEnd"))){       //如果为最后一个匹配规则,结束循环，返回匹配标识数
                    flag = true;       //结束标志位为true
                    if(SensitivewordFilter.MinMatchTYpe == matchType){    //最小规则，直接返回,最大规则还需继续查找
                        break;
                    }
                }
            }
            else{     //不存在，直接返回
                break;
            }
        }
        if(matchFlag < 2 && !flag){
            matchFlag = 0;
        }
        return matchFlag;
    }




    /**
     * 判断文字是否包含敏感字符
     *
     * @param txt       文字
     * @param matchType 匹配规则 1：最小匹配规则，2：最大匹配规则
     * @return 若包含返回true，否则返回false
     */
    public static boolean contains(String txt, int matchType) {
        boolean flag = false;
        for (int i = 0; i < txt.length(); i++) {
            int matchFlag = checkSensitiveWord(txt, i, matchType); //判断是否包含敏感字符
            if (matchFlag > 0) {    //大于0存在，返回true
                flag = true;
            }
        }
        return flag;
    }

}
```

