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