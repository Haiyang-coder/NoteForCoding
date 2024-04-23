# 通过继承WebMvcConfigurationSupport（springboot2.x后用此类） 类后重写addResourceHandlers

标题的知识点挺密集的,来一个一个分析
## 需求描述
> 用户将资源文件(如图片)存储到服务器上,用户使用url来访问资源文件,这里需要将资源文件的在电脑中的存储位置和url绑定.绑定的方法就是**标题**

接下来就是对标题中知识点的分析

### 1.WebMvcConfigurationSupport类
        是Spring MVC提供的配置类,常用于拦截器和资源处理功能
官网的描述是
>This is the main class providing the configuration behind the MVC Java config. **It is typically imported by adding @EnableWebMvc to an application @Configuration class.**  An alternative more advanced option is to extend directly from this class and override methods as necessary, remembering to add @Configuration to the subclass and @Bean to overridden @Bean methods. For more details see the javadoc of @EnableWebMvc.

### 1addResourceHandlers 
    我用它实现了资源绑定工作代码如下

```java
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/admin/**").addResourceLocations("classpath:/static/admin/");
        registry.addResourceHandler("/images/**")
                .addResourceLocations("file:" + MallCommon.FILE_SRC);
        registry.addResourceHandler("swagger-ui.html").addResourceLocations(
                "classpath:/META-INF/resources/");
        registry.addResourceHandler("/webjars/**").addResourceLocations(
                "classpath:/META-INF/resources/webjars/");
    }
```

我配置的静态资源路径是`file_src: /Users/sunhaiyang/webSrc/Pic/`, 
- 最后面的`/`不要忘了
- 最后面的`/`不要忘了
- 最后面的`/`不要忘了