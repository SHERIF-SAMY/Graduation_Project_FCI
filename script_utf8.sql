USE [master]
GO
/****** Object:  Database [db46830]    Script Date: 5/10/2026 6:23:46 PM ******/
CREATE DATABASE [db46830]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'db46830', FILENAME = N'D:\Services\MSSQL\Data\db46830.mdf' , SIZE = 73728KB , MAXSIZE = 1048576KB , FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'db46830_log', FILENAME = N'D:\Services\MSSQL\Data\db46830_log.ldf' , SIZE = 8192KB , MAXSIZE = 5242880KB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [db46830].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [db46830] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [db46830] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [db46830] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [db46830] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [db46830] SET ARITHABORT OFF 
GO
ALTER DATABASE [db46830] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [db46830] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [db46830] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [db46830] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [db46830] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [db46830] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [db46830] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [db46830] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [db46830] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [db46830] SET  ENABLE_BROKER 
GO
ALTER DATABASE [db46830] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [db46830] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [db46830] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [db46830] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [db46830] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [db46830] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [db46830] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [db46830] SET RECOVERY SIMPLE 
GO
ALTER DATABASE [db46830] SET  MULTI_USER 
GO
ALTER DATABASE [db46830] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [db46830] SET DB_CHAINING OFF 
GO
ALTER DATABASE [db46830] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [db46830] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [db46830] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [db46830] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
ALTER DATABASE [db46830] SET QUERY_STORE = ON
GO
ALTER DATABASE [db46830] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [db46830]
GO
/****** Object:  FullTextCatalog [db46830]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE FULLTEXT CATALOG [db46830] WITH ACCENT_SENSITIVITY = ON
AS DEFAULT
GO
/****** Object:  Table [dbo].[Categories]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Categories](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_Categories] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Subcategories]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Subcategories](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[CategoryId] [int] NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_Subcategories] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Products]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Products](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[CategoryId] [int] NOT NULL,
	[SubcategoryId] [int] NOT NULL,
	[LocationArea] [nvarchar](100) NOT NULL,
	[Condition] [int] NOT NULL,
	[ProductType] [nvarchar](100) NOT NULL,
	[Brand] [nvarchar](100) NOT NULL,
	[RentalGuarantee] [nvarchar](max) NOT NULL,
	[Name] [nvarchar](200) NOT NULL,
	[Description] [nvarchar](max) NOT NULL,
	[FinalPricePerDay] [decimal](10, 2) NOT NULL,
	[TermsConditions] [nvarchar](max) NOT NULL,
	[Status] [int] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[AverageRating] [float] NOT NULL,
	[BasePricePerDay] [decimal](10, 2) NOT NULL,
	[TotalReviews] [int] NOT NULL,
	[TotalPlatformProfit] [decimal](18, 2) NOT NULL,
	[TotalRentalCount] [int] NOT NULL,
	[RejectionReason] [nvarchar](max) NULL,
 CONSTRAINT [PK_Products] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProductImages]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProductImages](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[ProductId] [int] NOT NULL,
	[ImageUrl] [nvarchar](max) NOT NULL,
	[IsPrimary] [bit] NOT NULL,
 CONSTRAINT [PK_ProductImages] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[Products_LLm]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

        CREATE VIEW [dbo].[Products_LLm] AS
        SELECT
            p.Id,
            p.Name,
            p.Description,
            p.Brand,
            p.ProductType,
            p.LocationArea,
            p.Condition,
            p.FinalPricePerDay          AS PricePerDay,
            p.FinalPricePerDay,
            p.BasePricePerDay,
            p.Status,
            p.AverageRating,
            p.TotalReviews,
            p.TotalRentalCount,
            p.RentalGuarantee,
            p.TermsConditions,
            p.CreatedAt,
            p.CategoryId,
            c.Name                      AS CategoryName,
            p.SubcategoryId,
            sc.Name                     AS SubcategoryName,
            pi.ImageUrl                 AS ImageUrl
        FROM Products p
        LEFT JOIN Categories c        ON p.CategoryId    = c.Id
        LEFT JOIN Subcategories sc    ON p.SubcategoryId = sc.Id
        LEFT JOIN ProductImages pi    ON pi.ProductId = p.Id AND pi.IsPrimary = 1
    
GO
/****** Object:  Table [dbo].[__EFMigrationsHistory]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[__EFMigrationsHistory](
	[MigrationId] [nvarchar](150) NOT NULL,
	[ProductVersion] [nvarchar](32) NOT NULL,
 CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY CLUSTERED 
(
	[MigrationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetRoleClaims]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetRoleClaims](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[RoleId] [nvarchar](450) NOT NULL,
	[ClaimType] [nvarchar](max) NULL,
	[ClaimValue] [nvarchar](max) NULL,
 CONSTRAINT [PK_AspNetRoleClaims] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetRoles]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetRoles](
	[Id] [nvarchar](450) NOT NULL,
	[Name] [nvarchar](256) NULL,
	[NormalizedName] [nvarchar](256) NULL,
	[ConcurrencyStamp] [nvarchar](max) NULL,
 CONSTRAINT [PK_AspNetRoles] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetUserClaims]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetUserClaims](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[ClaimType] [nvarchar](max) NULL,
	[ClaimValue] [nvarchar](max) NULL,
 CONSTRAINT [PK_AspNetUserClaims] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetUserLogins]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetUserLogins](
	[LoginProvider] [nvarchar](450) NOT NULL,
	[ProviderKey] [nvarchar](450) NOT NULL,
	[ProviderDisplayName] [nvarchar](max) NULL,
	[UserId] [nvarchar](450) NOT NULL,
 CONSTRAINT [PK_AspNetUserLogins] PRIMARY KEY CLUSTERED 
(
	[LoginProvider] ASC,
	[ProviderKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetUserRoles]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetUserRoles](
	[UserId] [nvarchar](450) NOT NULL,
	[RoleId] [nvarchar](450) NOT NULL,
 CONSTRAINT [PK_AspNetUserRoles] PRIMARY KEY CLUSTERED 
(
	[UserId] ASC,
	[RoleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetUsers]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetUsers](
	[Id] [nvarchar](450) NOT NULL,
	[FullName] [nvarchar](max) NOT NULL,
	[NationalId] [nvarchar](450) NOT NULL,
	[IdCardImage] [nvarchar](max) NOT NULL,
	[AccountStatus] [int] NOT NULL,
	[Balance] [decimal](10, 2) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UserName] [nvarchar](256) NULL,
	[NormalizedUserName] [nvarchar](256) NULL,
	[Email] [nvarchar](256) NULL,
	[NormalizedEmail] [nvarchar](256) NULL,
	[EmailConfirmed] [bit] NOT NULL,
	[PasswordHash] [nvarchar](max) NULL,
	[SecurityStamp] [nvarchar](max) NULL,
	[ConcurrencyStamp] [nvarchar](max) NULL,
	[PhoneNumber] [nvarchar](max) NULL,
	[PhoneNumberConfirmed] [bit] NOT NULL,
	[TwoFactorEnabled] [bit] NOT NULL,
	[LockoutEnd] [datetimeoffset](7) NULL,
	[LockoutEnabled] [bit] NOT NULL,
	[AccessFailedCount] [int] NOT NULL,
	[City] [nvarchar](max) NULL,
	[Country] [nvarchar](max) NULL,
	[Iscertificated] [bit] NOT NULL,
	[LastLogin] [datetime2](7) NOT NULL,
	[governorate] [nvarchar](max) NULL,
	[sex] [nvarchar](max) NULL,
	[BlockReason] [nvarchar](max) NULL,
	[BlockedUntil] [datetime2](7) NULL,
	[RejectionReason] [nvarchar](max) NULL,
	[ImageUrl] [nvarchar](max) NULL,
 CONSTRAINT [PK_AspNetUsers] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AspNetUserTokens]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AspNetUserTokens](
	[UserId] [nvarchar](450) NOT NULL,
	[LoginProvider] [nvarchar](450) NOT NULL,
	[Name] [nvarchar](450) NOT NULL,
	[Value] [nvarchar](max) NULL,
 CONSTRAINT [PK_AspNetUserTokens] PRIMARY KEY CLUSTERED 
(
	[UserId] ASC,
	[LoginProvider] ASC,
	[Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatConversations]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatConversations](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[User1Id] [nvarchar](450) NOT NULL,
	[User2Id] [nvarchar](450) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[LastMessageAt] [datetime2](7) NULL,
	[LastMessagePreview] [nvarchar](max) NULL,
 CONSTRAINT [PK_ChatConversations] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatMessages]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatMessages](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[SenderId] [nvarchar](450) NOT NULL,
	[ReceiverId] [nvarchar](450) NOT NULL,
	[ProductId] [int] NULL,
	[Message] [nvarchar](max) NOT NULL,
	[IsRead] [bit] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[ConversationId] [int] NOT NULL,
 CONSTRAINT [PK_ChatMessages] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatReports]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatReports](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[MessageId] [int] NOT NULL,
	[ReporterId] [nvarchar](450) NOT NULL,
	[Reason] [nvarchar](max) NOT NULL,
	[Status] [int] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[AdminNote] [nvarchar](max) NULL,
	[ResolvedAt] [datetime2](7) NULL,
 CONSTRAINT [PK_ChatReports] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Favorites]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Favorites](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[ProductId] [int] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_Favorites] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Notifications]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Notifications](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[Title] [nvarchar](max) NOT NULL,
	[Body] [nvarchar](max) NOT NULL,
	[Data] [nvarchar](max) NULL,
	[IsRead] [bit] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[ReadAt] [datetime2](7) NULL,
 CONSTRAINT [PK_Notifications] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PlatformSettings]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PlatformSettings](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Key] [nvarchar](max) NOT NULL,
	[Value] [nvarchar](max) NOT NULL,
	[UpdatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_PlatformSettings] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProductReviews]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProductReviews](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[ProductId] [int] NOT NULL,
	[Score] [int] NOT NULL,
	[Comment] [nvarchar](max) NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UpdatedAt] [datetime2](7) NULL,
 CONSTRAINT [PK_ProductReviews] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProductStats]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProductStats](
	[ProductId] [int] NOT NULL,
	[TotalViews] [int] NULL,
	[TotalClicks] [int] NULL,
	[TotalFavorites] [int] NULL,
	[TotalRentRequests] [int] NULL,
	[LastUpdated] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RentalOrderDetails]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RentalOrderDetails](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[RentalOrderId] [int] NOT NULL,
	[StartDate] [datetime2](7) NOT NULL,
	[EndDate] [datetime2](7) NOT NULL,
	[DeliveryMethod] [int] NOT NULL,
	[City] [nvarchar](max) NOT NULL,
	[Street] [nvarchar](max) NOT NULL,
	[governorate] [nvarchar](max) NOT NULL,
 CONSTRAINT [PK_RentalOrderDetails] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RentalOrders]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RentalOrders](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[ProductId] [int] NOT NULL,
	[RenterId] [nvarchar](450) NOT NULL,
	[OwnerId] [nvarchar](450) NOT NULL,
	[Status] [int] NOT NULL,
	[TotalPrice] [decimal](10, 2) NOT NULL,
	[DeliveryFee] [decimal](10, 2) NOT NULL,
	[TotalAmount] [decimal](10, 2) NOT NULL,
	[TermsAgreed] [bit] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UpdatedAt] [datetime2](7) NULL,
 CONSTRAINT [PK_RentalOrders] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Reviews]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Reviews](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[ReviewerId] [nvarchar](450) NOT NULL,
	[RevieweeId] [nvarchar](450) NOT NULL,
	[RentalOrderId] [int] NOT NULL,
	[Score] [int] NOT NULL,
	[Comment] [nvarchar](max) NULL,
	[Status] [int] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UpdatedAt] [datetime2](7) NULL,
 CONSTRAINT [PK_Reviews] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Subscriptions]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Subscriptions](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
	[Price] [decimal](10, 2) NOT NULL,
	[DurationDays] [int] NOT NULL,
	[Features] [nvarchar](max) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_Subscriptions] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserAddresses]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserAddresses](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[AddressLine] [nvarchar](255) NOT NULL,
	[City] [nvarchar](100) NULL,
	[Area] [nvarchar](100) NULL,
	[IsDefault] [bit] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_UserAddresses] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserInteractions]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserInteractions](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](100) NULL,
	[SessionId] [nvarchar](100) NULL,
	[ProductId] [int] NULL,
	[ActionType] [nvarchar](50) NOT NULL,
	[SearchQuery] [nvarchar](500) NULL,
	[Category] [nvarchar](100) NULL,
	[Brand] [nvarchar](100) NULL,
	[LocationArea] [nvarchar](100) NULL,
	[PriceRange] [float] NULL,
	[PreferredLanguage] [nvarchar](10) NULL,
	[CreatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserSubscriptions]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserSubscriptions](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[SubscriptionId] [int] NOT NULL,
	[StartDate] [datetime2](7) NOT NULL,
	[EndDate] [datetime2](7) NOT NULL,
	[Status] [int] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_UserSubscriptions] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WalletTransactions]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WalletTransactions](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[Amount] [decimal](10, 2) NOT NULL,
	[Type] [int] NOT NULL,
	[ReferenceId] [int] NULL,
	[Description] [nvarchar](max) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_WalletTransactions] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WithdrawalRequests]    Script Date: 5/10/2026 6:23:48 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WithdrawalRequests](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [nvarchar](450) NOT NULL,
	[Amount] [decimal](18, 2) NOT NULL,
	[PhoneNumber] [nvarchar](max) NOT NULL,
	[Status] [int] NOT NULL,
	[RejectionReason] [nvarchar](max) NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[ProcessedAt] [datetime2](7) NULL,
 CONSTRAINT [PK_WithdrawalRequests] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AspNetRoleClaims_RoleId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_AspNetRoleClaims_RoleId] ON [dbo].[AspNetRoleClaims]
(
	[RoleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [RoleNameIndex]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [RoleNameIndex] ON [dbo].[AspNetRoles]
(
	[NormalizedName] ASC
)
WHERE ([NormalizedName] IS NOT NULL)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AspNetUserClaims_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_AspNetUserClaims_UserId] ON [dbo].[AspNetUserClaims]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AspNetUserLogins_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_AspNetUserLogins_UserId] ON [dbo].[AspNetUserLogins]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AspNetUserRoles_RoleId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_AspNetUserRoles_RoleId] ON [dbo].[AspNetUserRoles]
(
	[RoleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [EmailIndex]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [EmailIndex] ON [dbo].[AspNetUsers]
(
	[NormalizedEmail] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_AspNetUsers_AccountStatus]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_AspNetUsers_AccountStatus] ON [dbo].[AspNetUsers]
(
	[AccountStatus] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_AspNetUsers_NationalId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_AspNetUsers_NationalId] ON [dbo].[AspNetUsers]
(
	[NationalId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [UserNameIndex]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [UserNameIndex] ON [dbo].[AspNetUsers]
(
	[NormalizedUserName] ASC
)
WHERE ([NormalizedUserName] IS NOT NULL)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatConversations_User1Id_User2Id]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_ChatConversations_User1Id_User2Id] ON [dbo].[ChatConversations]
(
	[User1Id] ASC,
	[User2Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatConversations_User2Id]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatConversations_User2Id] ON [dbo].[ChatConversations]
(
	[User2Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatMessages_ConversationId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_ConversationId] ON [dbo].[ChatMessages]
(
	[ConversationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatMessages_ProductId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_ProductId] ON [dbo].[ChatMessages]
(
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatMessages_ReceiverId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_ReceiverId] ON [dbo].[ChatMessages]
(
	[ReceiverId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatMessages_SenderId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_SenderId] ON [dbo].[ChatMessages]
(
	[SenderId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatReports_MessageId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatReports_MessageId] ON [dbo].[ChatReports]
(
	[MessageId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatReports_ReporterId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatReports_ReporterId] ON [dbo].[ChatReports]
(
	[ReporterId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Favorites_ProductId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Favorites_ProductId] ON [dbo].[Favorites]
(
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Favorites_UserId_ProductId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Favorites_UserId_ProductId] ON [dbo].[Favorites]
(
	[UserId] ASC,
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Notifications_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Notifications_UserId] ON [dbo].[Notifications]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ProductImages_ProductId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ProductImages_ProductId] ON [dbo].[ProductImages]
(
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ProductReviews_ProductId_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_ProductReviews_ProductId_UserId] ON [dbo].[ProductReviews]
(
	[ProductId] ASC,
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ProductReviews_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_ProductReviews_UserId] ON [dbo].[ProductReviews]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Products_CategoryId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Products_CategoryId] ON [dbo].[Products]
(
	[CategoryId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Products_Status]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Products_Status] ON [dbo].[Products]
(
	[Status] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Products_SubcategoryId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Products_SubcategoryId] ON [dbo].[Products]
(
	[SubcategoryId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Products_UserId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_Products_UserId] ON [dbo].[Products]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RentalOrderDetails_RentalOrderId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_RentalOrderDetails_RentalOrderId] ON [dbo].[RentalOrderDetails]
(
	[RentalOrderId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_RentalOrders_OwnerId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_RentalOrders_OwnerId] ON [dbo].[RentalOrders]
(
	[OwnerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RentalOrders_ProductId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_RentalOrders_ProductId] ON [dbo].[RentalOrders]
(
	[ProductId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_RentalOrders_RenterId]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_RentalOrders_RenterId] ON [dbo].[RentalOrders]
(
	[RenterId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RentalOrders_Status]    Script Date: 5/10/2026 6:23:48 PM ******/
CREATE NONCLUSTERED INDEX [IX_RentalOrders_Status] ON [dbo].[RentalOrders]
(
	[Status] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Reviews_RentalOrderId_ReviewerId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Reviews_RentalOrderId_ReviewerId] ON [dbo].[Reviews]
(
	[RentalOrderId] ASC,
	[ReviewerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Reviews_RevieweeId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_Reviews_RevieweeId] ON [dbo].[Reviews]
(
	[RevieweeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Reviews_ReviewerId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_Reviews_ReviewerId] ON [dbo].[Reviews]
(
	[ReviewerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_Subcategories_CategoryId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_Subcategories_CategoryId] ON [dbo].[Subcategories]
(
	[CategoryId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UserAddresses_UserId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_UserAddresses_UserId] ON [dbo].[UserAddresses]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UI_Session]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_UI_Session] ON [dbo].[UserInteractions]
(
	[SessionId] ASC,
	[CreatedAt] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UI_User]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_UI_User] ON [dbo].[UserInteractions]
(
	[UserId] ASC,
	[CreatedAt] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_UserSubscriptions_SubscriptionId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_UserSubscriptions_SubscriptionId] ON [dbo].[UserSubscriptions]
(
	[SubscriptionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UserSubscriptions_UserId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_UserSubscriptions_UserId] ON [dbo].[UserSubscriptions]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_WalletTransactions_UserId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_WalletTransactions_UserId] ON [dbo].[WalletTransactions]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_WithdrawalRequests_UserId]    Script Date: 5/10/2026 6:23:49 PM ******/
CREATE NONCLUSTERED INDEX [IX_WithdrawalRequests_UserId] ON [dbo].[WithdrawalRequests]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[AspNetUsers] ADD  DEFAULT (CONVERT([bit],(0))) FOR [Iscertificated]
GO
ALTER TABLE [dbo].[AspNetUsers] ADD  DEFAULT ('0001-01-01T00:00:00.0000000') FOR [LastLogin]
GO
ALTER TABLE [dbo].[ChatMessages] ADD  DEFAULT ((0)) FOR [ConversationId]
GO
ALTER TABLE [dbo].[Products] ADD  DEFAULT ((0.0000000000000000e+000)) FOR [AverageRating]
GO
ALTER TABLE [dbo].[Products] ADD  DEFAULT ((0.0)) FOR [BasePricePerDay]
GO
ALTER TABLE [dbo].[Products] ADD  DEFAULT ((0)) FOR [TotalReviews]
GO
ALTER TABLE [dbo].[Products] ADD  DEFAULT ((0.0)) FOR [TotalPlatformProfit]
GO
ALTER TABLE [dbo].[Products] ADD  DEFAULT ((0)) FOR [TotalRentalCount]
GO
ALTER TABLE [dbo].[ProductStats] ADD  DEFAULT ((0)) FOR [TotalViews]
GO
ALTER TABLE [dbo].[ProductStats] ADD  DEFAULT ((0)) FOR [TotalClicks]
GO
ALTER TABLE [dbo].[ProductStats] ADD  DEFAULT ((0)) FOR [TotalFavorites]
GO
ALTER TABLE [dbo].[ProductStats] ADD  DEFAULT ((0)) FOR [TotalRentRequests]
GO
ALTER TABLE [dbo].[ProductStats] ADD  DEFAULT (getdate()) FOR [LastUpdated]
GO
ALTER TABLE [dbo].[RentalOrderDetails] ADD  DEFAULT (N'') FOR [City]
GO
ALTER TABLE [dbo].[RentalOrderDetails] ADD  DEFAULT (N'') FOR [Street]
GO
ALTER TABLE [dbo].[RentalOrderDetails] ADD  DEFAULT (N'') FOR [governorate]
GO
ALTER TABLE [dbo].[UserInteractions] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO
ALTER TABLE [dbo].[AspNetRoleClaims]  WITH CHECK ADD  CONSTRAINT [FK_AspNetRoleClaims_AspNetRoles_RoleId] FOREIGN KEY([RoleId])
REFERENCES [dbo].[AspNetRoles] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetRoleClaims] CHECK CONSTRAINT [FK_AspNetRoleClaims_AspNetRoles_RoleId]
GO
ALTER TABLE [dbo].[AspNetUserClaims]  WITH CHECK ADD  CONSTRAINT [FK_AspNetUserClaims_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetUserClaims] CHECK CONSTRAINT [FK_AspNetUserClaims_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[AspNetUserLogins]  WITH CHECK ADD  CONSTRAINT [FK_AspNetUserLogins_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetUserLogins] CHECK CONSTRAINT [FK_AspNetUserLogins_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[AspNetUserRoles]  WITH CHECK ADD  CONSTRAINT [FK_AspNetUserRoles_AspNetRoles_RoleId] FOREIGN KEY([RoleId])
REFERENCES [dbo].[AspNetRoles] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetUserRoles] CHECK CONSTRAINT [FK_AspNetUserRoles_AspNetRoles_RoleId]
GO
ALTER TABLE [dbo].[AspNetUserRoles]  WITH CHECK ADD  CONSTRAINT [FK_AspNetUserRoles_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetUserRoles] CHECK CONSTRAINT [FK_AspNetUserRoles_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[AspNetUserTokens]  WITH CHECK ADD  CONSTRAINT [FK_AspNetUserTokens_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[AspNetUserTokens] CHECK CONSTRAINT [FK_AspNetUserTokens_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[ChatConversations]  WITH CHECK ADD  CONSTRAINT [FK_ChatConversations_AspNetUsers_User1Id] FOREIGN KEY([User1Id])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[ChatConversations] CHECK CONSTRAINT [FK_ChatConversations_AspNetUsers_User1Id]
GO
ALTER TABLE [dbo].[ChatConversations]  WITH CHECK ADD  CONSTRAINT [FK_ChatConversations_AspNetUsers_User2Id] FOREIGN KEY([User2Id])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[ChatConversations] CHECK CONSTRAINT [FK_ChatConversations_AspNetUsers_User2Id]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_AspNetUsers_ReceiverId] FOREIGN KEY([ReceiverId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_AspNetUsers_ReceiverId]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_AspNetUsers_SenderId] FOREIGN KEY([SenderId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_AspNetUsers_SenderId]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_ChatConversations_ConversationId] FOREIGN KEY([ConversationId])
REFERENCES [dbo].[ChatConversations] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_ChatConversations_ConversationId]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_Products_ProductId] FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
ON DELETE SET NULL
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_Products_ProductId]
GO
ALTER TABLE [dbo].[ChatReports]  WITH CHECK ADD  CONSTRAINT [FK_ChatReports_AspNetUsers_ReporterId] FOREIGN KEY([ReporterId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ChatReports] CHECK CONSTRAINT [FK_ChatReports_AspNetUsers_ReporterId]
GO
ALTER TABLE [dbo].[ChatReports]  WITH CHECK ADD  CONSTRAINT [FK_ChatReports_ChatMessages_MessageId] FOREIGN KEY([MessageId])
REFERENCES [dbo].[ChatMessages] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ChatReports] CHECK CONSTRAINT [FK_ChatReports_ChatMessages_MessageId]
GO
ALTER TABLE [dbo].[Favorites]  WITH CHECK ADD  CONSTRAINT [FK_Favorites_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Favorites] CHECK CONSTRAINT [FK_Favorites_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[Favorites]  WITH CHECK ADD  CONSTRAINT [FK_Favorites_Products_ProductId] FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Favorites] CHECK CONSTRAINT [FK_Favorites_Products_ProductId]
GO
ALTER TABLE [dbo].[Notifications]  WITH CHECK ADD  CONSTRAINT [FK_Notifications_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Notifications] CHECK CONSTRAINT [FK_Notifications_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[ProductImages]  WITH CHECK ADD  CONSTRAINT [FK_ProductImages_Products_ProductId] FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ProductImages] CHECK CONSTRAINT [FK_ProductImages_Products_ProductId]
GO
ALTER TABLE [dbo].[ProductReviews]  WITH CHECK ADD  CONSTRAINT [FK_ProductReviews_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[ProductReviews] CHECK CONSTRAINT [FK_ProductReviews_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[ProductReviews]  WITH CHECK ADD  CONSTRAINT [FK_ProductReviews_Products_ProductId] FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ProductReviews] CHECK CONSTRAINT [FK_ProductReviews_Products_ProductId]
GO
ALTER TABLE [dbo].[Products]  WITH CHECK ADD  CONSTRAINT [FK_Products_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[Products] CHECK CONSTRAINT [FK_Products_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[Products]  WITH CHECK ADD  CONSTRAINT [FK_Products_Categories_CategoryId] FOREIGN KEY([CategoryId])
REFERENCES [dbo].[Categories] ([Id])
GO
ALTER TABLE [dbo].[Products] CHECK CONSTRAINT [FK_Products_Categories_CategoryId]
GO
ALTER TABLE [dbo].[Products]  WITH CHECK ADD  CONSTRAINT [FK_Products_Subcategories_SubcategoryId] FOREIGN KEY([SubcategoryId])
REFERENCES [dbo].[Subcategories] ([Id])
GO
ALTER TABLE [dbo].[Products] CHECK CONSTRAINT [FK_Products_Subcategories_SubcategoryId]
GO
ALTER TABLE [dbo].[RentalOrderDetails]  WITH CHECK ADD  CONSTRAINT [FK_RentalOrderDetails_RentalOrders_RentalOrderId] FOREIGN KEY([RentalOrderId])
REFERENCES [dbo].[RentalOrders] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[RentalOrderDetails] CHECK CONSTRAINT [FK_RentalOrderDetails_RentalOrders_RentalOrderId]
GO
ALTER TABLE [dbo].[RentalOrders]  WITH CHECK ADD  CONSTRAINT [FK_RentalOrders_AspNetUsers_OwnerId] FOREIGN KEY([OwnerId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[RentalOrders] CHECK CONSTRAINT [FK_RentalOrders_AspNetUsers_OwnerId]
GO
ALTER TABLE [dbo].[RentalOrders]  WITH CHECK ADD  CONSTRAINT [FK_RentalOrders_AspNetUsers_RenterId] FOREIGN KEY([RenterId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[RentalOrders] CHECK CONSTRAINT [FK_RentalOrders_AspNetUsers_RenterId]
GO
ALTER TABLE [dbo].[RentalOrders]  WITH CHECK ADD  CONSTRAINT [FK_RentalOrders_Products_ProductId] FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[RentalOrders] CHECK CONSTRAINT [FK_RentalOrders_Products_ProductId]
GO
ALTER TABLE [dbo].[Reviews]  WITH CHECK ADD  CONSTRAINT [FK_Reviews_AspNetUsers_RevieweeId] FOREIGN KEY([RevieweeId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[Reviews] CHECK CONSTRAINT [FK_Reviews_AspNetUsers_RevieweeId]
GO
ALTER TABLE [dbo].[Reviews]  WITH CHECK ADD  CONSTRAINT [FK_Reviews_AspNetUsers_ReviewerId] FOREIGN KEY([ReviewerId])
REFERENCES [dbo].[AspNetUsers] ([Id])
GO
ALTER TABLE [dbo].[Reviews] CHECK CONSTRAINT [FK_Reviews_AspNetUsers_ReviewerId]
GO
ALTER TABLE [dbo].[Reviews]  WITH CHECK ADD  CONSTRAINT [FK_Reviews_RentalOrders_RentalOrderId] FOREIGN KEY([RentalOrderId])
REFERENCES [dbo].[RentalOrders] ([Id])
GO
ALTER TABLE [dbo].[Reviews] CHECK CONSTRAINT [FK_Reviews_RentalOrders_RentalOrderId]
GO
ALTER TABLE [dbo].[Subcategories]  WITH CHECK ADD  CONSTRAINT [FK_Subcategories_Categories_CategoryId] FOREIGN KEY([CategoryId])
REFERENCES [dbo].[Categories] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Subcategories] CHECK CONSTRAINT [FK_Subcategories_Categories_CategoryId]
GO
ALTER TABLE [dbo].[UserAddresses]  WITH CHECK ADD  CONSTRAINT [FK_UserAddresses_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[UserAddresses] CHECK CONSTRAINT [FK_UserAddresses_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[UserSubscriptions]  WITH CHECK ADD  CONSTRAINT [FK_UserSubscriptions_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[UserSubscriptions] CHECK CONSTRAINT [FK_UserSubscriptions_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[UserSubscriptions]  WITH CHECK ADD  CONSTRAINT [FK_UserSubscriptions_Subscriptions_SubscriptionId] FOREIGN KEY([SubscriptionId])
REFERENCES [dbo].[Subscriptions] ([Id])
GO
ALTER TABLE [dbo].[UserSubscriptions] CHECK CONSTRAINT [FK_UserSubscriptions_Subscriptions_SubscriptionId]
GO
ALTER TABLE [dbo].[WalletTransactions]  WITH CHECK ADD  CONSTRAINT [FK_WalletTransactions_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[WalletTransactions] CHECK CONSTRAINT [FK_WalletTransactions_AspNetUsers_UserId]
GO
ALTER TABLE [dbo].[WithdrawalRequests]  WITH CHECK ADD  CONSTRAINT [FK_WithdrawalRequests_AspNetUsers_UserId] FOREIGN KEY([UserId])
REFERENCES [dbo].[AspNetUsers] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[WithdrawalRequests] CHECK CONSTRAINT [FK_WithdrawalRequests_AspNetUsers_UserId]
GO
USE [master]
GO
ALTER DATABASE [db46830] SET  READ_WRITE 
GO
