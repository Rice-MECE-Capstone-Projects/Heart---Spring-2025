/******************************************************************************
* Copyright (C) 2023 Advanced Micro Devices, Inc. All Rights Reserved.
* SPDX-License-Identifier: MIT
******************************************************************************/
/*
 * helloworld.c: simple test application
 *
 * This application configures UART 16550 to baud rate 9600.
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * ------------------------------------------------
 * | UART TYPE   BAUD RATE                        |
 * ------------------------------------------------
 *   uartns550   9600
 *   uartlite    Configurable only in HW design
 *   ps7_uart    115200 (configured by bootrom/bsp)
 */

#include <stdio.h>
#include <stdbool.h>
#include "platform.h"
#include "xil_printf.h"
#include "PDM_MIC_DRIVER.h"
#include "myip_read.h"
#include "xparameters.h"
#include "xintc.h"
#include "xtmrctr.h"
#include "sleep.h"
#include "xil_io.h"
#include "xgpio.h"



XGpio_Config *cfg_ptr;

/* Custom TIMER ---------------------------------------------------------------*/
XIntc    Intc;     //中断控制器实例
XTmrCtr  Timer_0, Timer_1;    //定时器实例

#define INTC_ID             XPAR_XINTC_0_BASEADDR   //中断控制器ID
#define XIL_EXCEPTION_ID_INT    16U                 //中断异常ID 
//Timer_0
#define TMRCTR_0_DEVICE_ID    XPAR_AXI_TIMER_0_BASEADDR //定时器中断ID
#define TMRCTR_0_INTR_ID      XPAR_FABRIC_XTMRCTR_0_INTR //定时中断ID
void timer_0_init(void);
void timer_0_intr_hander(void *InstancePtr,u8 Channel);
//Timer_1
#define TMRCTR_1_DEVICE_ID    XPAR_AXI_TIMER_1_BASEADDR //定时器中断ID
#define TMRCTR_1_INTR_ID      XPAR_FABRIC_XTMRCTR_1_INTR //定时中断ID
void timer_1_init(void);
void timer_1_intr_hander(void *InstancePtr,u8 Channel);
//KEY---------------------------------------------------------------
XGpio BTN_0_DEVICE,BTN_1_DEVICE;
#define BTN_0_ID XPAR_AXI_BTN_0_BASEADDR
#define BTN_1_ID XPAR_AXI_BTN_1_BASEADDR
#define BTN_0_MASK 0b1111
#define BTN_1_MASK 0b1111
#define DEBOUNCE_DELAY 0 // 消抖延迟
bool BTN_0_flag = 0;
bool BTN_1_flag = 0;
void button_init(void);
//LED---------------------------------------------------------------------------
XGpio LED_0_DEVICE,LED_1_DEVICE;
#define LED_0_ID XPAR_AXI_LED_0_BASEADDR
#define LED_1_ID XPAR_AXI_LED_1_BASEADDR
#define LED_0_MASK 0
#define LED_1_MASK 0
bool data = 0;  //LED  
void led_init(void);
//PDM_mic
volatile uint32_t DDR_flag = 0;
u32 DDR_flag_cache = 0;
volatile bool timer_flag = false;  // 全局标志位
u32 DDR_size = XPAR_MIG_0_HIGHADDRESS - XPAR_MIG_0_BASEADDRESS;
void pdm_mic_driver_init(void);
void result_output( u32 flag);

int main()
{
    //Initialization function--------------------------------------------------
    init_platform();
    led_init();
    button_init();
    pdm_mic_driver_init();
    xil_printf("PWM initialization succeeded！\n\r");
    xil_printf("DDR Size: %d \n\r",DDR_size);
    //Defined variable---------------------------------------------------------
    
    //Button Parameter Definition

    void handle_button_0(void);
    void handle_button_1(void);
    //DDR Parameter-----------------------------------------------------------
    
    //Function realization area------------------------------------------------
    // for(int i=0; i<6; i++)
    // {
    //     data = !data;
    //     XGpio_DiscreteWrite(&LED_0_DEVICE, 1, data);
    //     sleep(1);
    // }    

    xil_printf("Hello World\n\r");
    sleep(1);
    timer_0_init(); 
    timer_1_init(); 
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    while(1)
    {
        handle_button_0();  // 處理按鍵0
        handle_button_1();  // 處理按鍵1        
    }

    
    cleanup_platform();
    return 0;
}

// 按鍵0處理函數 (控制是否开始录制)
void handle_button_0(void)
{
    static u32 prev_data = 0;
    // static bool flag = 0;
    u32 data = XGpio_DiscreteRead(&BTN_0_DEVICE, 1);

    if (data != prev_data) {
        for (volatile int i = 0; i < DEBOUNCE_DELAY; i++) {}
        if (data != prev_data) {
            if (data != 0) {
                BTN_0_flag = !BTN_0_flag;
                if(BTN_0_flag) {
                    XTmrCtr_Stop(&Timer_0, 0);
                    XTmrCtr_Stop(&Timer_1, 0);
                    xil_printf("Microphone ON, start recording!\n\r");
                    
                    // 藍色LED快速閃爍兩次
                    u32 led_state = 0;
                    for(int i=0; i<4; i++) {
                        led_state = !led_state;
                        XGpio_DiscreteWrite(&LED_0_DEVICE, 1, led_state);
                        for(int j=0; j<50000; j++){}
                    }
                    DDR_flag = 0; //每次让记录从头开始，避免从之前记录的下一位存储空间继续，即覆盖之前录制了一半的信息
                    XTmrCtr_Start(&Timer_0, 0);
                } else {
                    XTmrCtr_Stop(&Timer_0, 0);
                    XTmrCtr_Stop(&Timer_1, 0);
                    xil_printf("Microphone OFF, stop recording!\n\r");
                  
                    // 藍色LED快速閃爍三次
                    u32 led_state = 0;
                    for(int i=0; i<6; i++) {
                        led_state = !led_state;
                        XGpio_DiscreteWrite(&LED_0_DEVICE, 1, led_state);
                        for(int j=0; j<50000; j++){}
                    }
                }
            }
            prev_data = data;
        }
    }
}
// 按鍵0處理函數 (控制是否开始传输)
void handle_button_1(void)
{
    static u32 prev_data = 0;
    // static bool flag = 0;
    u32 data = XGpio_DiscreteRead(&BTN_1_DEVICE, 1);

    if (data != prev_data) {
        for (volatile int i = 0; i < DEBOUNCE_DELAY; i++) {}
        if (data != prev_data) {
            if (data != 0) {
                BTN_1_flag = !BTN_1_flag;
                if(BTN_1_flag) {
                    XTmrCtr_Stop(&Timer_0, 0);
                    XTmrCtr_Stop(&Timer_1, 0);
                    xil_printf("Start Uploading!\n\r");
                  
                    // 紅色LED快速閃爍兩次
                    u32 led_state = 0;
                    for(int i=0; i<4; i++) {
                        led_state = !led_state;
                        XGpio_DiscreteWrite(&LED_1_DEVICE, 1, led_state);
                        for(int j=0; j<50000; j++){}
                    }
                    DDR_flag = 0; //每次让传输从头开始，避免从之前传输的下一位存储空间继续。
                    XTmrCtr_Start(&Timer_1, 0);
                } else {
                    XTmrCtr_Stop(&Timer_0, 0);
                    XTmrCtr_Stop(&Timer_1, 0);
                    xil_printf("Stop Uploading!\n\r");
                  
                    // 紅色LED快速閃爍三次
                    u32 led_state = 0;
                    for(int i=0; i<6; i++) {
                        led_state = !led_state;
                        XGpio_DiscreteWrite(&LED_1_DEVICE, 1, led_state);
                        for(int j=0; j<50000; j++){}
                    }
                }
            }
            prev_data = data;
        }
    }
}


void timer_0_init(void)
{
     //定时器初始化
    XTmrCtr_Initialize(&Timer_0, TMRCTR_0_DEVICE_ID);
    //为指定的计时器启用指定的选项。
    XTmrCtr_SetOptions(&Timer_0, 0,XTC_INT_MODE_OPTION |    //中断操作
                                 XTC_AUTO_RELOAD_OPTION | //自动加载
                                 XTC_DOWN_COUNT_OPTION);  //递减计数

    //设置指定计时器的重置值
    XTmrCtr_SetResetValue(&Timer_0, 0, 1);
    //设置计时器回调函数，指定的计时器满一个周期时驱动程序将调用该回调函数
    XTmrCtr_SetHandler(&Timer_0, timer_0_intr_hander,&Timer_0);
    //开启定时器
    // XTmrCtr_Start(&Timer_0, 0);
    //中断控制器初始化
    XIntc_Initialize(&Intc, INTC_ID);
    //关联中断源和中断处理函数
    XIntc_Connect(&Intc, TMRCTR_0_INTR_ID,
                 (XInterruptHandler)XTmrCtr_InterruptHandler,&Timer_0);
    //开启中断控制器
    XIntc_Start(&Intc, XIN_REAL_MODE);
    //使能中断控制器
    XIntc_Enable(&Intc, TMRCTR_0_INTR_ID);
        //设置并打开中断异常处理
    Xil_ExceptionInit();
        Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_INT,
                (Xil_ExceptionHandler)XIntc_InterruptHandler,
                &Intc);
        Xil_ExceptionEnable();
}

void timer_1_init(void)
{
     //定时器初始化
    XTmrCtr_Initialize(&Timer_1, TMRCTR_1_DEVICE_ID);
    //为指定的计时器启用指定的选项。
    XTmrCtr_SetOptions(&Timer_1, 0,XTC_INT_MODE_OPTION |    //中断操作
                                 XTC_AUTO_RELOAD_OPTION | //自动加载
                                 XTC_DOWN_COUNT_OPTION);  //递减计数

    //设置指定计时器的重置值
    XTmrCtr_SetResetValue(&Timer_1, 0, 1);
    //设置计时器回调函数，指定的计时器满一个周期时驱动程序将调用该回调函数
    XTmrCtr_SetHandler(&Timer_1, timer_1_intr_hander,&Timer_1);
    //开启定时器
    // XTmrCtr_Start(&Timer_1, 0);
    //中断控制器初始化
    XIntc_Initialize(&Intc, INTC_ID);
    //关联中断源和中断处理函数
    XIntc_Connect(&Intc, TMRCTR_1_INTR_ID,
                 (XInterruptHandler)XTmrCtr_InterruptHandler,&Timer_1);
    //开启中断控制器
    XIntc_Start(&Intc, XIN_REAL_MODE);
    //使能中断控制器
    XIntc_Enable(&Intc, TMRCTR_1_INTR_ID);
        //设置并打开中断异常处理
    Xil_ExceptionInit();
        Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_INT,
                (Xil_ExceptionHandler)XIntc_InterruptHandler,
                &Intc);
        Xil_ExceptionEnable();
}


void timer_0_intr_hander(void *InstancePtr,u8 Channel)  //回调函数
{
    XTmrCtr *TimerInstance = (XTmrCtr *)InstancePtr;
    //检测计数是否满一个周期
    if (XTmrCtr_IsExpired(TimerInstance, Channel))
    {        
        // xil_printf("Timer Test!\n\r");
        // xil_printf("Read: %d\n\r",MYIP_READ_mReadReg(XPAR_MYIP_READ_0_BASEADDR,MYIP_READ_S00_AXI_SLV_REG0_OFFSET));
        Xil_Out8(XPAR_MIG_0_BASEADDRESS + 100000 + DDR_flag, MYIP_READ_mReadReg(XPAR_MYIP_READ_0_BASEADDR,MYIP_READ_S00_AXI_SLV_REG0_OFFSET));  // 更新计数到外设
        // xil_printf("DDR_flag:%d\n\r",DDR_flag);
        DDR_flag ++;
        if(DDR_flag == 100000)
        {
            // u32 DDR_flag_cache = DDR_flag;
            DDR_flag = 0;
            xil_printf("Limited saving space!\n\r");
            xil_printf("Recording Finished!\n\r");
            // xil_printf("Output the result after the LED blinks two times!\n\r");
            XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0  
            XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1  
            for(int i=0; i<4; i++)     
            {
                data = !data;
                XGpio_DiscreteWrite(&LED_0_DEVICE, 1, data);
                XGpio_DiscreteWrite(&LED_1_DEVICE, 1, data);
                for(int j=0; j<50000; j++){}  
            }    
            xil_printf("To re-record, please press BTN0.|| To upload data, please press BTN1\n\r");
            BTN_0_flag = 0;
            BTN_1_flag = 0;
            // result_output(DDR_flag_cache);
        }
        
    }
}

void timer_1_intr_hander(void *InstancePtr,u8 Channel)  //回调函数
{
    XTmrCtr *TimerInstance = (XTmrCtr *)InstancePtr;
    //检测计数是否满一个周期
    if (XTmrCtr_IsExpired(TimerInstance, Channel)){
        // xil_printf("Timer Test!\n\r");
        // xil_printf("Read: %d\n\r",MYIP_READ_mReadReg(XPAR_MYIP_READ_0_BASEADDR,MYIP_READ_S00_AXI_SLV_REG0_OFFSET));
        xil_printf("Read:%d\n\r", Xil_In8(XPAR_MIG_0_BASEADDRESS + 100000 + DDR_flag));// 读取存储结果
        DDR_flag ++;
        if(DDR_flag == 100000)
        {
            xil_printf("Uploading Finished!\n\r");
            XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0  
            XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1  
            for(int i=0; i<6; i++)     
            {
                data = !data;
                XGpio_DiscreteWrite(&LED_0_DEVICE, 1, data);
                XGpio_DiscreteWrite(&LED_1_DEVICE, 1, data);
                for(int j=0; j<50000; j++){}  
            }   
            BTN_0_flag = 0;
            BTN_1_flag = 0;
        }
    }
    
}

void pdm_mic_driver_init(void)
{
    PDM_MIC_DRIVER_mWriteReg(XPAR_PDM_MIC_DRIVER_0_BASEADDR,PDM_MIC_DRIVER_S00_AXI_SLV_REG0_OFFSET,0x0001);
    PDM_MIC_DRIVER_mWriteReg(XPAR_PDM_MIC_DRIVER_0_BASEADDR,PDM_MIC_DRIVER_S00_AXI_SLV_REG1_OFFSET,17);
    PDM_MIC_DRIVER_mWriteReg(XPAR_PDM_MIC_DRIVER_0_BASEADDR,PDM_MIC_DRIVER_S00_AXI_SLV_REG2_OFFSET,2);
    PDM_MIC_DRIVER_mWriteReg(XPAR_PDM_MIC_DRIVER_0_BASEADDR,PDM_MIC_DRIVER_S00_AXI_SLV_REG3_OFFSET,1);
}

void button_init(void)
{
    // 配置BUTTON_0
    cfg_ptr = XGpio_LookupConfig(BTN_0_ID);
    XGpio_CfgInitialize(&BTN_0_DEVICE, cfg_ptr, cfg_ptr->BaseAddress);
    
    // 配置BUTTON_1
    cfg_ptr = XGpio_LookupConfig(BTN_1_ID);
    XGpio_CfgInitialize(&BTN_1_DEVICE, cfg_ptr, cfg_ptr->BaseAddress);
    
    // 设置数据方向为输入
    XGpio_SetDataDirection(&BTN_0_DEVICE, 1, BTN_0_MASK);
    XGpio_SetDataDirection(&BTN_1_DEVICE, 1, BTN_1_MASK);
}

void led_init(void)
{
    // 配置BUTTON_0
    cfg_ptr = XGpio_LookupConfig(LED_0_ID);
    XGpio_CfgInitialize(&LED_0_DEVICE, cfg_ptr, cfg_ptr->BaseAddress);
    
    // 配置BUTTON_1
    cfg_ptr = XGpio_LookupConfig(LED_1_ID);
    XGpio_CfgInitialize(&LED_1_DEVICE, cfg_ptr, cfg_ptr->BaseAddress);
    
    // 设置数据方向为输入
    XGpio_SetDataDirection(&LED_0_DEVICE, 1, LED_0_MASK);
    XGpio_SetDataDirection(&LED_1_DEVICE, 1, LED_1_MASK);
}

void result_output( u32 flag)
{
    xil_printf("END!!!\n\r");
    for(u32 i=0; i<flag; i++)
    {
        xil_printf("Read:%d\n\r", Xil_In8(XPAR_MIG_0_BASEADDRESS + 100000 + i));// 读取存储结果
    }
    XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0  
    XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1   
    return;
}

// XGpio KEY_0_DEVICE,KEY_1_DEVICE;
// XGpio_Config *cfg_ptr;
// #define KEY_0_ID XPAR_AXI_GPIO_0_BASEADDR
// #define KEY_1_ID XPAR_AXI_GPIO_1_BASEADDR
// #define KEY_0_MASK 0b1111
// #define KEY_1_MASK 0b1111


// volatile uint32_t ii = 0;

// int main() {


//     u32 DDR_size = XPAR_MIG_0_HIGHADDRESS - XPAR_MIG_0_BASEADDRESS;
//     timer_0_init(); 
//     xil_printf("Recording Start!\r\n");
//     // for(u32 i=0;i<50000000;i++)
//     // {


//     // }
//     xil_printf("Recording Finish!\r\n");
//     cleanup_platform();
//     return 0;
// }

    // while(1)
    // {

        // // 读取按键数据
        // data_0 = XGpio_DiscreteRead(&BTN_0_DEVICE, 1);
        // data_1 = XGpio_DiscreteRead(&BTN_1_DEVICE, 1);
        
        // // 去抖并判断按键按下事件
        // if (data_0 != prev_data_0) {
        //     for (volatile int i = 0; i < DEBOUNCE_DELAY; i++) {}  // 延时消抖
        //     if (data_0 != prev_data_0) {  // 确保按键状态稳定
        //         if (data_0 != 0) 
        //         {
        //             BTN_0_flag = !BTN_0_flag;
        //             if(BTN_0_flag) 
        //             {   
        //                 XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0
        //                 XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1
        //                 xil_printf("Microphone ON!\n\r");
        //                 //蓝色LED快速闪两下
        //                 data = 0;
        //                 for(int i=0; i<4; i++)
        //                 {
        //                     data = !data;
        //                     XGpio_DiscreteWrite(&LED_0_DEVICE, 1, data);
        //                     for(int j=0; j<50000; j++){}                  
        //                 }
        //                 XTmrCtr_Start(&Timer_0, 0);//开启定时器0
        //             }
        //             else 
        //             {
        //                 // xil_printf("Microphone OFF!\n\r");
        //                 XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1
        //                 XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0
        //                 xil_printf("Microphone OFF!\n\r");
        //                 //蓝色LED快速闪三下
        //                 data = 0;
        //                 for(int i=0; i<6; i++)
        //                 {
        //                     data = !data;
        //                     XGpio_DiscreteWrite(&LED_0_DEVICE, 1, data);
        //                     for(int j=0; j<50000; j++){}    
        //                 }
        //             }
        //         }
        //         prev_data_0 = data_0;  // 更新前一状态
        //     }
        // }
        
        // if (data_1 != prev_data_1) {
        //     for (volatile int i = 0; i < DEBOUNCE_DELAY; i++) {}  // 延时消抖
        //     if (data_1 != prev_data_1) 
        //     {  // 确保按键状态稳定
        //         if (data_1 != 0) 
        //         {
        //             BTN_1_flag = !BTN_1_flag;
        //             if(BTN_1_flag) 
        //             {   
        //                 // xil_printf("DDR_flag:%d\n\r",DDR_flag);
        //                 XTmrCtr_Stop(&Timer_0, 0);//先关闭定时器0
        //                 xil_printf("Start recording!\n\r");
        //                 //红色LED快速闪两下
        //                 data = 0;
        //                 for(int i=0; i<4; i++)
        //                 {
        //                     data = !data;
        //                     XGpio_DiscreteWrite(&LED_1_DEVICE, 1, data);
        //                     for(int j=0; j<50000; j++){}                  
        //                 }
        //                 // XTmrCtr_Start(&Timer_0, 0);//开启定时器0
        //                 XTmrCtr_Start(&Timer_1, 0);//开启定时器1
                        
        //             }
        //             else 
        //             {
        //                 // xil_printf("Stop recording!\n\r");
        //                 XTmrCtr_Stop(&Timer_1, 0);//关闭定时器1
        //                 XTmrCtr_Stop(&Timer_0, 0);//关闭定时器0
        //                 xil_printf("Stop recording!\n\r");
        //                 //红色LED快速闪三下
        //                 data = 0;
        //                 for(int i=0; i<6; i++)
        //                 {
        //                     data = !data;
        //                     XGpio_DiscreteWrite(&LED_1_DEVICE, 1, data);
        //                     for(int j=0; j<50000; j++){}    
        //                 }
        //             }
        //         }
        //         prev_data_1 = data_1;  // 更新前一状态
        //     }
        // }
    // }