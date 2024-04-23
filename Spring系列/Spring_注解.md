#  Spring 注解开发的常用注解
**定义bean**
> @Component
> @Controller
> @Service
> @Repository(这个包括上面的都可以加别名)

**纯注解开发**
>@Configuration (相当于之前之前xml的功能)
>@ComponentScan (指定扫描bean的范围)
>依然用AnnotationConfigApplicationContext方法来加载,不过方法的参数是吧配置类的Class对象传入

**bean的作用范围和模式**
>@Scope(这个指定单例还是非单例,一般都是单例)

**bean的生命周期**
>@PostConstruct(初始化方法的注释)
>@PreDestory(销毁方法的注释)

**自动配装**
>@Autowired(自动配装引用类型)
>@Qualifier(指定配装的bean)
>@Value(指定基本数据类型的值,一般用占位符)

**读取properties配置文件**
>@PropertySource(加上配置文件的名字)

**管理第三方的bean**
>@Bean()将第三方的bean以方法的形式定义,并用@Bean注释
>@Import,在Configuration的类上添加该注释,参数是第三方的Bean所在的类

**为第三方的Bean倒入参数(引用类型和简单类型)**
>基本数据类型:可以和@Value配合,定义变量,从配置文件中读取,在传给第三方的Bean
>引用数据类型:在第三方的Bean的方法参数中设置需要注入的数据类型,会直接注入已经在IOC容器中的对象

**AOP**
>@Aspect告诉Spring这个类是通知类
>@PointCut通知类中的切点,用来限制作用的连接点
>@before设置通知的执行时间(参数是切入点),写在通知上
>@EnableAspectJAutoProxy,写在Spring的配置类中,告诉Spring用了AOP编程

**Junit整合Spring**
>@RunWith()类运行器,Spring整合JUnit专用的
>@ContextConfigration(Class=)参数是Spring的配置类

**Spring整合Mybatis**
>1. 新建一个mybatis的配置类,他的作用就相当于mybatis的xml配置文件,mybatis贴心的准备了模版类sqlDessionFactoryBean,这个类就是为了生成sqlSessionFactory对象
>2. 在Bean中添加完sqlSessionFactory后在添加一个Mapper对象

**通知类注解**
>@before,JoinPoint参数可以获取连接点的参数
>@After
>**@Around**，ProceedingJoinPoint参数代表原始方法的调用，而且这个对象有连接点的各种信息.连接点有返回值的话，需要把通知的返回值改成连接点的返回值（一般是Object）并且Return回去来代替你原始方法的返回值.
>@AfterReturning,这个注解可以获取到连接点返回值,用参数中的returnning参数搞定
>@AfterThrowing,抛出异常后才运行

**ProceedingJoinPoint**
>这里单独说一下这个对象,因为能获取连接点的各种信息,那么他也可以修改连接点的信息,如传入的参数,返回的返回值,从而对连接点的输出造成影响.因为之后环绕通知需要操作目标对象所以只有环绕通知才会用到这个对象.

**Spring事务管理**
>1. Spring的事务管理器是基于JDBC的实物管理来做的,即开启事务,提交实物,Spring整合之后有下面几个注释
>2. 因为是依靠的JDBC提供的事务管理,所以要在JDBC的config里面加载一个Bean,PlatformtransactionManager接口和实现它的transactionManager.在构建事务管理器的时候,用到了dataSource对象,这个dataSource在构建Jdbc的时候也用到过,mybatisconfig传入的参数也有这个必须注意需要用同一个对象,即Bean用的单例模式
```java
   @Bean
   public DataSource dataSource(){
       DruidDataSource druidDataSource = new DruidDataSource();
       druidDataSource.setDriverClassName(driver);
       druidDataSource.setUrl(url);
       druidDataSource.setUsername(username);
       druidDataSource.setPassword(password);

       return druidDataSource;
   }
   //代码可以看出,这个DataSource对象是用来链接数据库,也可以解释开启事务用到的DataSource是用这个

```


>@EnableTransactionManagement,这个注解放在SpringConfig类上,告诉Spring开启了事务
@Transactional,在要开启事务的Service层接口的方法上,表示这个操作要开启事务功能.里面有一个参数**propagation**在业务层接口的方法可以用这个参数决定是否加入另一个事

**常用的事务的配置**
>![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/action.png)
>注意图片上的**rollbackFor**,JDBC默认只有运行时异常(**NULLponitException,算术运算异常和Error**)才会回滚

**propagation参数**
>![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/dsf.png)
