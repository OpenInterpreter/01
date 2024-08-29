# 01 Light Manufacturing Report
![alt text](<Assets/01 Report Header.png>)
## Table of Contents
- [Introduction](#introduction)
- [Product Requirements](#product-requirements)
- [Firmware Design](#firmware-design)
- [Electrical Design](#electrical-design)
- [User Experience + Industrial Design](#user-experience-industrial-design)
- [Appendix](#appendix)

## Introduction
This report captures the comprehensive work completed through June 2024, including detailed product requirements, product architecture, design thinking, and strategic decisions. Below, you'll find links to essential assets, resources, and documentation that collectively support the development and vision of the O1 Light.

Thanks to [Facture](https://facture.design) for the amazing work producing these resources.

## Product Requirements

 
[Project Details](<Assets/01_Light_PRD_Project_Details.png>) 

The Product Requirements Document (PRD) is the north star during development and includes additional information such as success metrics and risks/mitigations. It is critical that this is drafted early on in any project and maintained diligently throughout. Requirements are categorized and utilize priority ranking (P0/P1/P2) to focus on core function, but not forgetting about reach goals or long-term product targets.

The following summarize the content that is present in the PRD:  


### Product Requirements


| #  | Feature                      | Requirement                                                              | Priority | Notes                                                                   |
|----|------------------------------|--------------------------------------------------------------------------|----------|-------------------------------------------------------------------------|
| 1  | System Requirements          | Full device COGs should be <$70, <$45, <$30                              | P0, P1, P2| Updated per kickoff                                                     |
| 2  | Functional Requirements - UX/ID | General size must be around the size of a Glossier You                  | P1       |                                                                         |
|    |                              | Thumbprint indentation on top of the case                                | P0       |                                                                         |
|    |                              | Silicon wrapper/skin around the main mechanical enclosure                | P1       | To be determined upon manufacturing vendor clarifying information       |
|    |                              | Silicone wrapper surface should be pleasant to hold                      | P1       | STEM Player as inspiration                                              |
|    |                              | Thumbprint size and orientation must cater to appropriate device orientation | P0   |                                                                         |
|    |                              | Device case must fit comfortably within the vast majority of consumers' hands | P0   |                                                                         |
|    |                              | Users must be able to easily access and plug in a USB C cord to charge   | P0       |                                                                         |
|    |                              | Tactile button to engage voice transmission                              | P0       |                                                                         |
|    |                              | Haptic vibration must be detectable to user while in hand and pocket     | P1       |                                                                         |
|    |                              | LED must be perceivable to user in daylight                              | P2       | May or may not be included in the device                                |
| 3  | Functional Requirements - Mechanical | No larger than <55 x 55 x 38> mm                                     | P0       | No larger than current prototype                                        |
|    |                              | No heavier than <50> g                                                   | P2       | Baseline of an AirPods case - open for discussion                       |
|    |                              | All component parts shall be located and secured to avoid chatter       | P0       |                                                                         |
|    |                              | Pad printing shall meet the requirements of Abrasion and Adhesion        | P1       | Should this be branded?                                                 |
|    |                              | Date of manufacture marking on the exterior of the housing               | P1       | Indelible and uniquely identified                                       |
|    |                              | PROTOTYPE – not for resale                                               | P1       |                                                                         |
| 4  | Functional Requirements - Electrical | Device shall be capable of communicating with server via Bluetooth    | P0       |                                                                         |
|    |                              | Device shall be capable of communicating with server via Wifi            | P1       |                                                                         |
|    |                              | Audio output should be clear and discernible from an arm’s length away   | P0       |                                                                         |
|    |                              | Device shall be audible from 12-18" away in quiet environment            | P1       | User is expected to need to bring device closer in noisy environments   |
|    |                              | Speaker driver shall be capable of delivering at least xx Watts of power | P0       | 01 Light has 2.5W speaker driver but no listed speaker                  |
|    |                              | Speaker driver must have no more than xx % THD                           | P0       |                                                                         |
|    |                              | Shall be capable of producing an acoustic sound pressure level (SPL) of at least xx dB at 10 cm | P0 |                                                                         |
|    |                              | Microphone shall have SNR of at least 61.5 dB(A)                         | P0       | Driven from 01 Light components                                         |
|    |                              | Microphone shall have sensitivity of at least -19 dBFS (94dB SPL @ 1 kHz)| P0       | Driven from 01 Light components                                         |
|    |                              | Tactile pushbutton shall have an operating force of at least xx gf       | P1       |                                                                         |
|    |                              | Battery should provide at least 4 hours of active Bluetooth use          | P0       |                                                                         |
|    |                              | Battery should provide at least 2 hours of active WiFi use               | P0       |                                                                         |
|    |                              | Device should provide haptic feedback to user                            | P1       |                                                                         |
|    |                              | User must be able to charge battery via USB-C port                       | P0       |                                                                         |
|    |                              | Installing FW updates should be possible via USB-C port                  | P1       |                                                                         |
|    |                              | Device may contain LED to indicate status of charge                      | n/a      | Client expects one more discussion (with Killian included) about this   |
|    |                              | Device may leverage Bluetooth headset for speaker and microphone         | P2       |                                                                         |
| 5  | Functional Requirements - Firmware | Device shall disable WiFi when Bluetooth is used                      | P2       | ESP supports simultaneous connections, however, device should have capabilities of turning the unused or lower speed connection off to conserve power. |
|    |                              | Microphone shall never be enabled unless pushbutton is pressed           | P0       |                                                                         |
|    |                              | Device shall deliver unique tones and/or vibration to alert user of low power and fully charged states | P1 | Specific UX alert requirements TBD                                      |
|    |                              | User should be able to turn the device ON/OFF by quickly pressing the pushbutton 3 times | P1 | quickly needs more definition                                           |
|    |                              | Device should be capable of simultaneous charging and operation          | P1       |                                                                         |
|    |                              | Security of data transfer shall be considered only after all P0 items are complete | P1 |                                                                         |
| 6  | Functional Requirements - Software |                                                                     | n/a      |                                                                         |
| 7  | Environmental Requirements   | Ambient temperatures of <-15°C, 45°C>                                    | P0       |                                                                         |
|    |                              | Ambient temperatures of <-30°C, 50°C>                                    | P0       |                                                                         |
|    |                              | Ambient relative humidity of <10%, 90%>                                  | P0       |                                                                         |
|    |                              | Ambient relative humidity of <10%, 90%>                                  | P0       |                                                                         |
|    |                              | 0 to 10,000 feet steady-state                                            | P0       |                                                                         |
|    |                              | Airplane transit – Pressure change of 0 ft to 8,000 ft (2 hr dwell) to 0 ft with a ramp rate of 250 ft/min | P0 | Device must remain in off state                                         |
|    |                              | IP53                                                                     | P0       | Minimal use case - going out in the rain                                |
|    |                              | IP65                                                                     | P1       | Expected use case                                                       |
|    |                              | Drop from 30” – no permanent damage to the device                        | P0       | Some cosmetic damage is acceptable                                      |
|    |                              | Drop from 60” – no permanent damage to the device                        | P1       | Some cosmetic damage is acceptable                                      |
|    |                              | Visual color change no greater than Slight after exposure using UVA-351 lamps for 200 hours | P1 | Corresponding to 8 on the ASTM scale of 0 (Very Severe) to 10 (No Effect) after exposure using UVA-351 lamps for 200 hours (Test per ASTM D4674-02A, Method IV) |
|    |                              | Device shall withstand wiping with mild soap or detergent and water      | P0       | No functional or cosmetic damage                                        |
|    |                              | No substantial staining or cosmetic defect from household cleaners       | P1       |                                                                         |
|    |                              | USB connector                                                            | P1       |                                                                         |
|    |                              | The device shall not contain materials which sustain fungus growth       | P1       |                                                                         |
| 8  | Safety and Regulatory        | The surface temperature of the product does not exceed <75 degC> during any use case (e.g. charging & being used) | P0 | Derived off of a plastic enclosure and available standards              |
| 9  | Other                        | The packaging will protect the device and all other items from drop of <5ft> | P0 | All packaging requirements to be discussed in next meeting to determine who is owning this. |
|    |                              | The final packaging will include instructions for use                    | P0       |                                                                         |
|    |                              | The final product will include a 01 Light, Charger, Power Brick          | P0       |                                                                         |
|    |                              | The device should be presented or revealed in a visually appealing way upon initial unboxing | P1 |                                                                         |

 
## Electrical Design
 

### Electrical Design Approach
Electrical hardware design follows on requirements definition with the creation of a system block diagram and selection of key components for each block. Key components were selected based on ability to meet requirements, as well as other key criteria such as component size, availability, and minimizing development risk. This major component selection is to be followed by schematic capture, PCB layout, PCBA manufacture, and test.

To support a tight development timeline and requirements for wireless communication, a MCU module providing required radio functions with a transferable FCC certification was targeted. Selecting a module that provided desired support for both Bluetooth/BLE and Wi-Fi with the required certification for handheld (“portable”) devices proved to be challenging, leading to a strategy of extending the existing certification for a non-handheld device through a change in ID. In order to minimize cost and overhead of this approach, portable certification was to be obtained by limiting RF transmit power in firmware to a level that provided exemption from SAR testing.
 

### Hardware Block Diagram
<div style="text-align: center;">
    <img src="Assets/Hardware Block Diagram.png" style="width:80%;">
</div>

### Component Selection - Overview
Due to proposed speed of development, component selection had to be completed quickly and without any significant error. The following priorities were considered while selecting electrical components:

1. **Minimizing risk** to schedule
   - Classified design elements into high and low risk categories based on the following:
     - Priority of the feature it supports (P0, P1, P2)
     - Confidence in ability to select the right component the first time, without testing
     - Impact to system if component needs to be re-spec'd
   - Overspec’d components to ensure performance requirements would be easily achieved
2. **Speed** of selection and development
   - Did not always exhaust every available option if subsystem was low enough risk and suitable options were already found
   - Considered hardware and firmware development implications when appropriate, opted for well supported ICs with existing driver libraries
3. **Size** of component and associated design
   - Carefully reviewed size of each component and proposed solutions to make sure design would meet space constraints


### Wireless Module Selection
Selection: [ESP32-PICO-MINI-02](https://www.espressif.com/sites/default/files/documentation/esp32-pico-mini-02_datasheet_en.pdf)  


Key Criteria: Wi-Fi & BLE/BT Classic Support, I2S Interface

Justification:
- Supports BT Classic which is needed to stream audio with iPhones
- Previously used chipset with well documented libraries available

| MFR       | PRODUCT #                                                                 | IC               | LxWxH (mm)     | Est. Cost  | Ipeak Tx/Rx (mA) | CFR 2.1093 | BT VERSION | BT CLASSIC | WIFI | AUDIO | NATIVE USB? | Notes                                                              |
|-----------|--------------------------------------------------------------------------|------------------|----------------|-------|------------------|------------|------------|------------|------|-------|-------------|--------------------------------------------------------------------|
| Infineon  | [CYBT-413061-02](https://www.digikey.com/en/products/detail/infineon-technologies/CYBT-413061-02/16894635) | CYW20719         | 12 x 16.3 x 1.7 | $14.70 |                | Yes        | 5          | Yes        | *No*   | I2S   | ?           |                                                                    |
| Ezurio    | [BT860-SA](https://www.digikey.com/en/products/detail/ezurio/BT860-SA/8251359)                             | CYW20704         | 12.9 x 8.5 x 2.2 | $9.86  |                | *Yes*        | 5          | Yes        | *No*   | I2S   | No          | Certification info not totally clear from publicly available info |
| Infineon  | [CYBT-343026-01](https://www.digikey.com/en/products/detail/infineon-technologies/CYBT-343026-01/9477838)  | CYW20706         | 15 x 15.5 x 1.95 | $8.63  |                | Yes        | 4.2        | Yes        | *No*   | I2S   |             |                                                                    |
| Microchip | [BM64SPKS1MC2-0001A](https://www.digikey.com/en/products/detail/microchip-technology/BM64SPKS1MC2-0001AA/6152253) | IS2062           | 15 x 29 x 2.5    | $12.71 |                | Yes        | 5          | Yes        | *No*   | I2S   |    No         | Size larger than desired, integrates battery charger               |
| Ezurio    | [453-00052R](https://www.digikey.com/en/products/detail/ezurio/453-00052R/14320013)                        | nRF5340          | 10 x 15 x 2.2    | $10.91 | 9.1/8.6        | ***Yes***        | 5.2        | *No*         | *No*   | I2S   | ?           |                                                                    |
| Silicon   | [BGM113A256V21R](https://www.digikey.com/en/products/detail/silicon-labs/BGM113A256V21R/7201263)           | EFR32BG          | 9.15 x 15.7 x 1.9| $11.51 |                | Yes        | 4.2        | *No*         | *No*   | I2S   | No          |                                                                    |
| Ezurio    | [453-00005](https://www.digikey.com/en/products/detail/ezurio/453-00005/9608588)                           | nRF52810         | 10 x 14 x 2.2    | $6.41  | 15.4/10        | Yes        | 5          | *No*         | *No*   | PDM   |      ?       | PDM input only                                                     |
| ESP       | [ESP32-S3-MINI-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf) | ESP32-S3         | 15.4 × 20.5 × 2.4 |       | 355/97         | No         | 5          | *No*         | Yes  | I2S   |     Yes        |                                                                    |
| ESP       | [ESP32-C3-MINI-1](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf) | ESP32-C3         | 13.2 x 16.6 x 2.4 |       | 350/82         | No         | 5          | No         | Yes  | I2S   |     Yes        |                                                                    |
| **ESP**       | **[ESP32-PICO-MINI-02](https://www.espressif.com/sites/default/files/documentation/esp32-pico-mini-02_datasheet_en.pdf)** | **ESP32-PICO**       |** 13.2 × 16.6 × 2.4** | **$3.50** | **368/117**        | ***No***         |**4.2**        | **Yes**        | **Yes**  | **I2S**   |     **No**        |                                                                    |


### Regulatory Approach Summary & Costs
- **Exposure**:
  - Module survey revealed lack of pre-certified modules supporting BT/BLE and Wi-Fi for “Portable” use cases
    - Several BT/BLE only options identified
    - Lack of Wi-Fi options attributed to typically higher transmit power
  - **Strategy**: Obtain Change of ID + Class II Permissive Change for Portable Certification
    - **SAR Testing**: Demonstrates exposure compliance for portable use, but test is costly and time consuming
    - **Transmit Power Exemption**: Provides a shorter path to certification with performance trade-off
      - Initial calculation indicated that Exemption could be acquired for transmit powers <10dBm
    - See [KDB 447498 D01 General RF Exposure Guidance v06](https://apps.fcc.gov/kdb/GetAttachment.html?id=f8IQgJxTTL5y0oRi0cpAuA%3D%3D&desc=447498%20D01%20General%20RF%20Exposure%20Guidance%20v06&tracking_number=20676) for detailed information

- **Emissions**:
  - Self Declaration of Conformity
  - Intentional Radiator Testing & Unintentional Radiator Testing

> #### Regulatory Costs
>
> | Vendor               | Unintentional Radiator Testing | Intentional Radiator Testing | Administrative Fees | SAR Testing  | Total (Excluding SAR) | Total (Including SAR) |
> |----------------------|-------------------------------|-----------------------------|---------------------|--------------|-----------------------|-----------------------|
> | CKC Laboratories     | $1,720                        | $1,720                      | $4,350              | $7,550**     | $7,790                | $15,340               |
> | Element              | $2,962                        | $6,105                      | $5,395              | $29,752      | $14,462               | $44,214               |
>
> **Unverified estimate

 

### Audio Subsystem
- **Speaker**
  - Considered **high risk** due to highest priority (P0) designation, size constraints, and significant impact to mechanical design should speaker need to be respec’d
  - Performance improvements from the existing prototype were among the most important for this component
  - Prioritized speaker component survey so that samples may be ordered and tested

- **Amplifier**
  - Considered **low risk** due to confidence in ability to spec IC that meets performance requirements
  - I2S interface limited available options

- **Microphone**
  - Considered **low risk** due to our ability to identify microphone used in existing prototype which informed specifications
    - *Client was satisfied incumbent microphone performance*
  - I2S interface limited available options


### Speaker Selection
Selection: [OWS-142037TA-4](https://www.digikey.com/en/products/detail/ole-wolff-electronics-inc/OWS-142037TA-4/22471770)

Key Criteria: Efficiency (dB SPL), Size, Rated Power

Justification:
- Fit within size constraints, best available option with respect to efficiency and rated power specs

| MFR       | PRODUCT #            | IMPEDANCE (Ω) | POWER RATED (W) | dB(A) SPL | RES FREQ (Hz) | LxWxH (mm) | MOUNTING | TERMINATION | IP | PRICE (QTY 1) | PRICE (QTY 100) | NOTES          |
|-----------|----------------------|----------------|-----------------|------------|---------------|-------------|----------|-------------|----|---------------|-----------------|----------------|
| PUI Audio | [SMS-1804MS-HT](https://www.mouser.com/ProductDetail/PUI-Audio/SMS-1804MS-HT?qs=mELouGlnn3fl03BnLM1Xhg%3D%3D)        | 4              | 1               | 96         | 950           | 18 x 18 x 5.9 | PCB Mount | SMD         | 67 | $4.51         | $3.02           |                |
| CUI Devices| [CMS-15118C-SP](https://www.digikey.com/en/products/detail/cui-devices/CMS-15118C-SP/7404549)       | 8              | 0.8             | 88         | 850           | 15 x 11 x 3  | Board Mount | Spring      | -  | $1.81         | $1.40           |                |
| CUI Devices| [CMS-18138A-SP](https://www.digikey.com/en/products/detail/cui-devices/CMS-18138A-SP/7404547)       | 8              | 0.8             | 92         | 1k            | 18 x 13 x 2.5| Board Mount | Spring      | -  | $2.50         | $1.68           |                |
| CUI Devices| [CMS-15118D-L100](https://www.digikey.com/en/products/detail/cui-devices/CMS-15118D-L100/7404551)     | 8              | 0.7             | 91         | 950?          | 15 x 11 x 3  | Board Mount | Wire Leads  | -  | $2.83         | $1.90           |                |
| CUI Devices| [CDS-1328-16-SP](https://www.digikey.com/en/products/detail/cui-devices/CDS-1328-16-SP/15851265?s=N4IgTCBcDaIMIBEDKBaAjAZjADnQNhSQAUQBdAXyA)      | 16             | 0.2             | 85         | 1.1k          | 13 x 13 x 2.8| Board Mount | Pads        | -  | $1.76         | $1.19           |                |
| PUI Audio | [AS01508MS-WP](https://www.digikey.com/en/products/detail/pui-audio-inc/AS01508MS-WP/21531554?s=N4IgTCBcDaIAQEEDKAGAjAVhQDgLJIFoB1ABRAF0BfIA)         | 8              | 1               | 95         | 950           | 15 x 11 x 3  | PCB Mount | SMD         | 65 | $2.37         | $1.60           |                |
| DB Unlimited| [SM160908-1](https://www.mouser.com/ProductDetail/DB-Unlimited/SM160908-1?qs=t9M3m0YJX4McRQsIxFAblw%3D%3D)         | 8              | 0.5             | 96         | 900           | 16 x 16 x 3.3| Flush Mount| Wire Leads  | -  | $2.32         | $1.55           | N/A DigiKey    |
| Toaglas   | [SPKM.17.8.A](https://www.mouser.com/ProductDetail/Taoglas/SPKM.17.8.A?qs=t7xnP681wgUs1zZxKb4XJQ%3D%3D)          | 8              | 0.5             | 96         | 900           | 17 x 17 x 4.4| Frame Mount| Wire Leads  | -  | $2.38         | $2.27           |                |
| CUI Devices| [CDM-16008](https://www.mouser.com/ProductDetail/CUI-Devices/CDM-16008?qs=WyjlAZoYn51nEqcAYSp0lA%3D%3D)           | 8              | 0.4             | 93         | 500           | 16 x 16 x 3.2| Board Mount | Pads        | -  | $1.58         | $1.20           |                |
| CUI Devices| [CDMG15008-03A](https://www.mouser.com/ProductDetail/CUI-Devices/CDMG15008-03A?qs=WyjlAZoYn51x0KDsSVXvZQ%3D%3D)       | 8              | 0.3             | 92         | 900           | 15 x 15 x 2.8| Board Mount | Pads        | -  | $1.77         | $1.37           | OOS DigiKey    |
| CUI Devices| [CMS-251405-24SP-X8](https://www.digikey.com/en/products/detail/cui-devices/CMS-251405-24SP-X8/18742621?s=N4IgTCBcDaIMIFkDKBaMBWAjAFgAzrWyQAUUANADhAF0BfIA)  | 4              | 2               | 103        | 950           | 25 x 14 x 5  || Solder Pads| X8           | $2.78         | $1.87           |                |
| CUI Devices| [CMS-251437-24SP-X8](https://www.digikey.com/en/products/detail/cui-devices/CMS-251437-24SP-X8/22521369?s=N4IgTCBcDaIMIFkDKBaMBWAjAFgMwHY1skAFFADQA4QBdAXyA)  | 4              | 2               | 103        | 950           | 25 x 14 x 5  || Solder Pads| X8           | $2.97         | $2.00           |                |
| CUI Devices| [CMS-231137-158SP-X8](https://www.digikey.com/en/products/detail/cui-devices/CMS-231137-158SP-X8/18742604?s=N4IgTCBcDaIMIFkDKBaMBmAjJ9B2FmArABxIAKKAGsSALoC%2BQA) | 8              | 1.5             | 103        | 1000          | 23 x 11 x 3.7|| Solder Pads| X8          | $2.35         | $1.58           |                |
| Challenge | [CS18-02P110-03-1X](https://www.digikey.com/en/products/detail/challenge-electronics/CS18-02P110-03-1X/16537896)    | 4              | 2               | 104        | 1100          | 18 x 16 x 3.7|| Solder Pads| 67          | $3.03         | $2.04           |                |
|**Ole Wolff**| **[OWS-142037TA-4](https://www.digikey.com/en/products/detail/ole-wolff-electronics-inc/OWS-142037TA-4/22471770)**       | **4**              | **2**               | **104.5**      | **1050**          | **20 x 14 x 3.7**|| **Solder Pads**| **67**           | **$1.34**         | **$0.92**           |                |
| CUI Devices| [CMS-1535-058SP](https://www.digikey.com/en/products/detail/cui-devices/CMS-1535-058SP/22521359?s=N4IgTCBcDaIMIFkDKBaAjAVgMwZQBgwA4kAFEAXQF8g)      | 8              | 0.5             | 96         | 1000          | 15 x 15 x 3.5|| Solder Pads| -           | $1.82         | $1.23           |                |


### Speaker Driver Selection
Selection: [MAX98357AEWL+T](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX98357AEWL-T/4271383?s=N4IgjCBcpgbFoDGUBmBDANgZwKYBoQB7KAbRAGYAGAVljGpAF0CAHAFyhAGU2AnASwB2AcxABfMQQBMpEAFkAggA0AnAA5y1AOwKmYoA)

Key Criteria: Output Power, Digital Interface

Justification:
- Well supported libraries available
- More than 3x the output power from prototype component
- Very small footprint needed for complete design

| MFR       | PRODUCT #                                                                 | DIMENSIONS (mm) | PRICE (QTY 100) | VOLTAGE (V) | POWER (W) | INTERFACE | NOTES                                |
|-----------|---------------------------------------------------------------------------|-----------------|-----------------|-------------|-----------|-----------|--------------------------------------|
| **ADI**       | **[MAX98357AEWL+T](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX98357AEWL-T/4271383?s=N4IgjCBcpgbFoDGUBmBDANgZwKYBoQB7KAbRAGYAGAVljGpAF0CAHAFyhAGU2AnASwB2AcxABfMQQBMpEAFkAggA0AnAA5y1AOwKmYoA)**         | **1.4 x 1.5 x 0.5** | **$2.10**           | **2.5 - 5.5**   | **3.2**       | **I2S**       | **Driver libraries available, well supported IC** |
| NXP       | [TFA9879HN](https://www.digikey.com/en/products/detail/nxp-usa-inc/TFA9879HN-N1-157/2406246)              | 4 x 4 x 1       | $1.80           | 2.5 - 5.5   | 2.75      | I2S       |                                      |
| TI        | [TAS2110RPPT](https://www.digikey.com/en/products/detail/texas-instruments/TAS2110RPPT/11502243)            | 4.5 x 4 x 1     | $2.36           | 1.65 - 1.95 | 6.1       | I2S       | Integrated boost, designed to be used with battery - may need large caps? |
| ADI       | [SSM2537ACBZ-R7](https://www.digikey.com/en/products/detail/analog-devices-inc/SSM2537ACBZ-R7/3777447)         | 1.2 x 1.2 x 0.3 | $2.42           | 2.5 - 5.5   | 2.7       | I2S       |                                      |


### Microphone Selection
Selection: [SPH0645LM4H-B](https://www.digikey.com/en/products/detail/knowles/SPH0645LM4H-B/5332440)

Key Criteria: SNR, Output Protocol

Justification:
- Matched or exceeded (SNR) all specs from incumbent mic used in prototype
- Port location was of mild concern but plan was to design in flexibility to pivot to top facing port if needed

| MFR       | PRODUCT #              | DIMENSIONS (mm) | PRICE (QTY 100) | SNR (dB)    | DIRECTION    | OUTPUT    | VOLTAGE (V) | CURRENT (mA) | PORT LOCATION | NOTES           |
|-----------|------------------------|-----------------|-----------------|-------------|--------------|-----------|-------------|--------------|---------------|-----------------|
| Knowles   | [SPM1423HM4H-B](https://www.digikey.com/en/products/detail/knowles/SPM1423HM4H-B/3621630?s=N4IgTCBcDaIMoAUCyBGALGAzACSW7AtAEIgC6AvkA)          | 4.72 x 3.76 x 1.4| -               | 61.5        | Omnidirectional| PDM       | 1.6 - 3.6   | 0.6          | Top           | Used in client's prototype, obsolete |
| DB Unlimited| [MM042602-15](https://www.digikey.com/en/products/detail/db-unlimited/MM042602-15/9962860)          | 4 x 3 x 1.1     | $2.10           | 65          | Omnidirectional| PDM       | 1.6 - 3.6   | 0.64         | Top           | No I2S mics w top port, PDM might be viable |
| **Knowles**   | [**SPH0645LM4H-B**](https://www.digikey.com/en/products/detail/knowles/SPH0645LM4H-B/5332440)          | **3.5 x 2.65 x 1.1**| **$1.49**           | **65**          | **Omnidirectional**| **I2S**       | **1.62 - 3.6**  | **0.6**          | **Bottom**        |                 |
| TDK       | [ICS-43434](https://www.digikey.com/en/products/detail/tdk-invensense/ICS-43434/6140298)              | 3.5 x 2.65 x 0.98| $1.72           | 64          | Omnidirectional| I2S       | 1.65 - 3.63 | 0.55         | Bottom        |                 |
| PUI       | [DMM-4026-B-I2S-R](https://www.digikey.com/en/products/detail/pui-audio-inc/DMM-4026-B-I2S-R/11587483)       | 4 x 3 x 1.1     | $1.78           | 64          | Omnidirectional| I2S       | 1.5 - 3.6   | 1            | Bottom        |                 |
| TDK       | [ICS-43432](https://www.digikey.com/en/products/detail/tdk-invensense/ICS-43432/5252320)              | 4 x 3 x 1.1     | $1.97           | 65          | Omnidirectional| I2S       | 1.62 - 3.63 | 1.5          | Bottom        |                 |



### UI Subsystem
- **Haptic Driver**
  - Considered **low risk** due to priority (P1) designation
  - Needed to consider various motor types (ERM, LRA) and prioritized components supported with existing driver libraries

- **Haptic Motor**
  - Considered **low risk** due to priority (P1) designation and abundance of options
  - Decided to select this component after speaker, battery, and PCBA outline were determined so that remaining space could be used to consider suitable candidates

- **Pushbutton & LED**
  - Considered **low risk** due to confidence in ability to spec components that meets performance requirements


### Haptic Driver and Motor
Selection: [DA7280-00V42](https://www.digikey.com/en/products/detail/renesas-electronics-corporation/DA7280-00V42/10474889) (Driver), TBD Motor

Key Criteria: Force (Motor), Rated Output (Driver)

Justification:
- Plenty of output drive (500mA max), supports wide frequency range

| ROLE   | MFR       | PRODUCT #             | DIMENSIONS (mm) | PRICE (QTY 100) | TYPE    | RPM    | FREQ   | V_RATED (V) | I_MAX (mA) | FORCE (Grms) | NOTES            |
|--------|-----------|-----------------------|-----------------|-----------------|---------|--------|--------|-------------|------------|--------------|------------------|
| MOTOR  | PUI Audio | [HD-EMC1003-2-LW15-R](https://www.digikey.com/en/products/detail/pui-audio-inc/HD-EMC1003-2-LW15-R/16522090)   | 10 x 10 x 2.7   | $1.55           | ERM     | 13000  | -      | 3           | 85         | ?            |                  |
|| Vybronics| [VC1018B001L](https://www.digikey.com/en/products/detail/vybronics-inc/VC1018B001L/9974295)                    | 10 x 10 x 1.8   | $1.78           | ERM     | 13500  | -      | 3.2         | 85         | 0.4          |                  |
|| Vybronics| [VC1020B327F](https://www.digikey.com/en/products/detail/vybronics-inc/VC1020B327F/9356386)                    | 10 x 10 x 2.1   | $2.31           | ERM     | 1350   | -      | 3           | 85         | 0.7          |                  |
|| Vybronics| [VW0825AB001G](https://www.digikey.com/en/products/detail/vybronics-inc/VW0825AB001G/9974284)                   | 8 x 8 x 2.5     | $3.00           | ERM     | 14000  | -      | 3           | 90         | 1            | BLDC             |
|| Vybronics| [VC0720B001F](https://www.digikey.com/en/products/detail/vybronics-inc/VC0720B001F/6009905)                    | 7 x 7 x 2       | $2.37           | ERM     | 10000  | -      | 3           | 85         | 0.3          |                  |
|| Vybronics| [VCLP0820B004L](https://www.digikey.com/en/products/detail/vybronics-inc/VCLP0820B004L/10285889)                  | 8 x 8 x 2.1     | $2.31           | ERM     | 9000   | -      | 3           | 35         | 0.25         |                  |
|| Vybronics| [VC0820B006F](https://www.digikey.com/en/products/detail/vybronics-inc/VC0820B006F/6009906?s=N4IgTCBcDaIAQDUDCAGAHGFAhFKBsAYgDoAuIAugL5A)                    | 8 x 8 x 2.1     | $2.44           | ERM     | 10000  | -      | 3           | 85         | 0.3          |                  |
|| Vybronics| [VG0640001D](https://www.digikey.com/en/products/detail/vybronics-inc/VG0640001D/15220805)                     | 6 x 6 x 4       | $3.33           | LRA     | -      | 210    | 1.8         | 75         | 0.9          |                  |
|| Vybronics| [VG0832014L](https://www.digikey.com/en/products/detail/vybronics-inc/VG0832014L/16376022)                      | 8 x 8 x 3.2    | $2.35           | LRA     | -      | 235    | 1.8         | 80         | 1            | [AlternateA](https://www.digikey.com/en/products/detail/vybronics-inc/VG0832014L/16376022), [AlternateB](https://www.vybronics.com/coin-vibration-motors/lra/v-g0832014l) |
|| Vybronics| [VLV101040A](https://www.digikey.com/en/products/detail/vybronics-inc/VLV101040A/12323590)                     | 10 x 10 x 4     | $4.35           | LRA     | -      | 170    | 2.5         | 350        | 2.75         |                  |
| DRIVER | TI        | [DRV2605LYZFR](https://www.digikey.com/en/products/detail/texas-instruments/DRV2605LYZFR/4866959)          | 1.47 x 1.47 x 0.28 | $1.71        | ERM/LRA | -      | 125 - 300    | -     | ?            | - |
|  | **Renesas**   | **[DA7280-00V42](https://www.digikey.com/en/products/detail/renesas-electronics-corporation/DA7280-00V42/10474889)**        | **1.35 x 1.75 x 0.55** |**$0.73** | **ERM/LRA** | -  | **50 - 300**    | **5.5**      | **500**      | - |


### Power Subsystem

- **Battery**
  - Considered **high risk** due to highest priority (P0) designation, size constraints, and significant impact to mechanical design should battery need to be respec’d
  - Improving single charge battery life was among most important requirements for new design
  - Likely needed to pursue custom battery pack design to meet performance and space requirements

- **Charger**
  - Considered **low risk** due to confidence in ability to spec IC that meets performance requirements

- **Switching Regulators**
  - Considered **high risk** due to potential for switching noise to negatively impact radio subsystem
  - Buck regulator (3V3) needed for system-wide power
    - Spec’d to easily handle full system load current (IOUT ≥ 1A)
    - Variable output was favored to accommodate worst case dropout voltage (VDO)
  - Boost regulator (5VO) provisioned for in case speaker amplifier is not powerful enough with 3V3
    - Could not be known for sure until final enclosure and audio were used for testing

- **Linear Regulator**
  - Considered **low risk** due to confidence in ability to spec IC that meets performance requirements


### Battery and Charger

Battery
No selection made yet, working with the following suppliers to find a pack that fits space constraints:
- Ampere Power, VCELL Power, PHD Energy, LiPol, Nova, Grepow

Charger
Selection: [MCP73871T-2CCI/ML](https://www.digikey.com/en/products/detail/microchip-technology/MCP73871-2CCI-ML/1680971)

Key Criteria: Supports Load Sharing

Justification:
- Stayed with incumbent option and opted out of extensive component surveying for this part in favor of other more critical design elements


### Power Regulators

Selection: [TPS62824](https://www.digikey.com/en/products/detail/texas-instruments/TPS62824ADMQR/14004408) (Buck), [TPS61202DRCT](https://www.digikey.com/en/products/detail/texas-instruments/TPS61202DRCT/1536200) (Boost), [NCP187AMT330TAG](https://www.digikey.com/en/products/detail/onsemi/NCP187AMT330TAG/10273441) (LDO)

Key Criteria: Efficiency, Output Current & Voltage, PSRR

Justification:
- Buck & Boost were chosen based on highest efficiency
- LDO was chosen based on combination of relatively low VDO and sufficiently high IOUT

| TYPE  | MFR         | PRODUCT #                                                                 | DIMENSIONS (mm)   | COST (QTY 100) | VIN (V) | VOUT (V) | F_SW (MHz) | EFFICIENCY | IOUT (mA) | VDO (mV) | PSRR (dB) | NOTES                                         |
|-------|-------------|---------------------------------------------------------------------------|-------------------|----------------|---------|----------|------------|------------|-----------|----------|-----------|-----------------------------------------------|
| BUCK  | TI          | [TPS62808YKAR](https://www.digikey.com/en/products/detail/texas-instruments/TPS62808YKAR/10434691)           | 1 x 0.7 x 0.25    | $0.62          | 1.8-5.5 | 1.8-3.3  | 1.5        | 94-97%     | 600       | -        | -         | Constant f_sw = reduces RF interference but lower efficiency at light loads |
|   | TI          | [TPS62849DLCR](https://www.digikey.com/en/products/detail/texas-instruments/TPS62849DLCR/10445066)           | 2 x 1.5 x 1       | $0.98          | 1.8-6.5 | 3.4      | 1.8        | 90-97%     | 750       | -        | -         |                                               |
|   | Microchip   | [MCP1603T-330I/OS](https://www.digikey.com/en/products/detail/microchip-technology/MCP1603T-330I-OS/1098431)       | 2.8 x 2.9 x 1     | $1.00          | 2.7 - 5.5| 3.3     | 2          | 75-95%     | 500       | -        | -         |                                               |
|   | TI          | [TPS62080DSGR](https://www.digikey.com/en/products/detail/texas-instruments/TPS62080DSGR/2797957)           | 2 x 2 x 0.7       | $1.19          | 2.3 - 6 | Variable | 2          | 85-95%     | 1200      | -        | -         |                                               |
| | **TI**          | **[TPS62824DMQR](https://www.digikey.com/en/products/detail/texas-instruments/TPS62824DMQR/16181961?s=N4IgTCBcDaICoAUDKA2MAOMAWAIgWQEUQBdAXyA)**           | **1.5 x 1.5 x 1**     | **$0.70**          | **2.4 - 5.5**| **Variable**| **2.2**        | **93-97%**     | **1000**      | **-**        | **-**         |                                               |
|   | TI          | [TPS62237DRYT](https://www.digikey.com/en/products/detail/texas-instruments/TPS62237DRYT/2202273)           | 1 x 1.5 x 0.6     | $1.11          | 2.05 - 6| 3.3      | 2          | 87-95%     | 500       | -        | -         | Suitable for linear regulator replacement     |
| BOOST | TI          | [TPS610997YFFR](https://www.digikey.com/en/products/detail/texas-instruments/TPS610997YFFR/6580123)          | 1.23 x 0.88 x 0.5 | $0.76          | 0.7 - 5.5| 5       | Dynamic    | 90-95%     | 800       | -        | -         | Dynamic f_sw for high efficiency at low loads |
|  | TI          | [TPS61240YFFT](https://www.digikey.com/en/products/detail/texas-instruments/TPS61240YFFT/2057748)           | 1.29 x 0.89 x 0.5 | $0.76          | 2.3 - 5.5| 5       | 3.5        | 83-93%     | 450       | -        | -         |                                               |
|  | ADI         | [MAX8969EWL50+T](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX8969EWL50-T/5086437)         | 1.26 x 1.26 x 0.45| $1.30          | 2.5 - 5.5| 5       | 3          | 86-95%     | 700       | -        | -         |                                               |
|  | onsemi      | [FAN48610UC50X](https://www.digikey.com/en/products/detail/onsemi/FAN48610UC50X/4555489)          | 1.25 x 1.25 x 0.4 | $0.61          | 2.5 - 4.8| 5       | 2.5        | 70-92%     | 1000      | -        | -         | Very low efficiency at less than 10 mA        |
|  | Microchip   | [MCP1642BT-50I/MC](https://www.digikey.com/en/products/detail/microchip-technology/MCP1642BT-50I-MC/5137686)       | 2 x 3 x 1         | $1.00          | 0.65 - 5.5| 5      | 1          | 45-95%     | 800       | -        | -         | "Low noise, Anti-Ringing control"             |
| | **TI**          | **[TPS61202DRCR](https://www.digikey.com/en/products/detail/texas-instruments/TPS61202DRCR/1908017)**           | **3 x 3 x 0.8**       | **$1.32**          | **0.3 - 5.5**| **5**       | **1.25 - 1.65**| **80-93%**     | **800**       | **-**        | **-**         | **Option to turn off power-saving mode and reduce emissions spread** |
| LDO   | onsemi      | [NCP176AMX330TCG](https://www.digikey.com/en/products/detail/onsemi/NCP176AMX330TCG/5761739)        | 1.25 x 1.25 x 0.5 | $0.17          | 5.5     | 3.3      | -          | -          | 500       | 165      | 75 (1 kHz)|                                               |
|    | TI          | [LP5912-3.3DRVR](https://www.digikey.com/en/products/detail/texas-instruments/LP5912-3-3DRVR/6005673)         | 2 x 2 x 0.8       | $0.82          | 6.5     | 3.3      | -          | -          | 500       | 180      | 75 (100 Hz)|                                               |
|    | onsemi      | [NCV8189CMTWADJTAG](https://www.digikey.com/en/products/detail/onsemi/NCV8189CMTWADJTAG/22031481?s=N4IgTCBcDaIHIGEBqAOAjCgnAgsgFQHUBBAEQCk8iBxEAXQF8g)      | 2 x 2 x 0.7       | $0.51          | 5.5     | 3.3      | -          | -          | 500       | 129      | 85 (1 kHz)|                                               |
|    | onsemi      | [NCP161AMX330TBG](https://www.digikey.com/en/products/detail/onsemi/NCP161AMX330TBG/5257729)        | 0.67 x 0.67 x 0.26| $0.24          | 5.5     | 3.3      | -          | -          | 450       | 260      | 70? (1kHz)|                                               |
|    | Microchip   | [MIC94345-SYMT-TR](https://www.digikey.com/en/products/detail/microchip-technology/MIC94345-SYMT-TR/3728492)       | 1.6 x 1.6 x 0.5   | $0.36          | 3.6     | 3.3      | -          | -          | 500       | 200      | ??        |                                               |
|   | **onsemi**      | **[NCP187AMT330TAG](https://www.digikey.com/en/products/detail/onsemi/NCP187AMT330TAG/10273441)**        | **2 x 2 x 0.8**       | **$0.44**          | **5.5**     | **3.3**      | **-**          | **-**          | **1200**      | **220**      | **75**        |                                               |


## Firmware Design

### Firmware Development Approach
Firmware development is initiated by defining the requirements and choosing the appropriate hardware platform. For this project, we have selected the [ESP32-PICO-MINI-02](https://www.espressif.com/sites/default/files/documentation/esp32-pico-mini-02_datasheet_en.pdf). To facilitate the development process and ensure alignment with the user interface design, we document the program flow, state transitions, and critical error handling within a comprehensive set of flow charts.

As the existing prototype already included Wi-Fi functionality, defining the function of the Bluetooth/BLE link profile to be used and rationalizing this against available libraries for the target platform is also a critical task. Selecting and setting up the development environment enables code drafting and testing to begin.

### Firmware Flow Charts
<p align="center">
  <img src="Assets/Firmware Flow Charts.png" alt="Firmware Flow Charts" width="80%"/>
</p>

### Firmware Development
- **Bluetooth Profile**
  - BLE Audio Profile: Investigated for low energy consumption and solid embedded system support, unable to utilize due to lack of iOS support
  - BT Classic Profiles ([A2DP](https://github.com/pschatzmann/ESP32-A2DP), [HFP](https://github.com/bluekitchen/btstack), HSP): Not fit to application or lacking in royalty-free open-source library support
  - Plan of Record: Utilize [BLE GATT](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/esp_gatts.html) to transfer data packets similar to Wi-Fi implementation, essentially generating custom profile
    - Requires coordination with mobile app developer to support custom profile

- **Development Environment**
  - PlatformIO: Espressif discontinued support for PlatformIO, latest version of ESP-IDF not available ([#1225](https://github.com/platformio/platform-espressif32/issues/1225))
    - I2S drivers in older version of IDF caused audio issues when interfacing with other libraries
    - Some success using [audio-tools library](https://github.com/pschatzmann/arduino-audio-tools) by Phil Schatzmann
  - Plan of Record: Develop in VSCode using ESP-IDF extension for v5.3 library support


### User Experience + Industrial Design

Identifying the most streamlined user interactions and device feedback is crucial to maintaining the integrity of the experience using the O1 Light. This was done through an in-depth exploration of unique user inputs, main device use cases, error states, and various edge cases within the context of larger user flows. Identification of haptic / visual / auditory feedback for each interaction helped to understand the ability for a user to interact with the device using very simple inputs.

In addition, collaboration with electrical and mechanical engineering resulted in various high-level device form constraints and helped to understand color, material, and finish options to be had through various manufacturing techniques.

## Industrial Design Approach

### User Interface / Workflow
- Identified the main user flow + auxiliary flows for user interaction points
- Determined inputs required to progress interaction
- Reviewed how the device should respond to user inputs, communicate error states, etc.

### Main User Flow
<p align="center">
  <img src="Assets/Main User Flow.png" alt="Main User Flow" width="80%"/>
</p>


### Identified Auxiliary User Flows

**Charging / Pairing**

<p align="center">
  <img src="Assets/Charging & Pairing.png" alt="Charging & Pairing" width="80%"/>
</p>

**Volume / Speaker Interrupt**

<p align="center">
  <img src="Assets/Volume & Speaker Interrupt.png" alt="Volume & Speaker Interrupt" width="80%"/>
</p>


### User Inputs + Device Feedback

#### Power and Prompt Actions
| Action / State                      | User Input                              | Device Feedback                                                                            |
|-------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------|
| Power On                            | Press and hold thumb button for 3 s     | Haptics, Auditory Tone, white LED on (then off after tbd time)                             |
| Power Off                           | Press thumb button then press and hold for 3 s | Haptics, Auditory Tone, white LED on then turns off                                         |
| Woken From Sleep + Begin Prompt Dictation | Press and hold thumb button              | Haptics upon successful wake + connection (indicating ready to speak) - would typically be ~1s tbd |
| End Prompt Dictation                | Release thumb button                    | Haptics                                                                                   |
| Prompt Response                     | NA                                      | Auditory language model generated response                                                |
| Error State                         | NA                                      | Triple haptics, red LED, tbd audio response (error codes, etc. to be determined)           |

#### Charging and Pairing Actions
| Action / State                      | User Input                              | Device Feedback                                                                            |
|-------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------|
| Charging Begun                      | USB C Cable Inserted                    | Haptics, Auditory Tone, LED on indicating charge level                                     |
| Charging Finished                   | NA                                      | LED cycles through red, amber, and green until full                                       |
| Enter Pairing Mode                  | Press thumb button 5X                   | Haptics, auditory tone, LED flashes blue                                                  |
| App Setup Procedures                | TBD (need to get app developer inputs)  | TBD (need to get app developer inputs)                                                    |
| Device Paired Successfully          | NA                                      | Haptics, White LED                                                                        |

#### Volume and Speaker Actions
| Action / State                      | User Input                              | Device Feedback                                                                            |
|-------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------|
| Volume Prompting                    | Using main interaction flow, user requests volume change verbally | Haptics, Auditory Tone, white LED on (then off after tbd time)                              |
| Volume Response / Setting           | NA                                      | Haptic response when setting is altered, auditory LLM response to prompt in volume set    |
| Speaker Interrupt + Battery Status  | Press and release thumb button          | Current prompt response cancelled, LED displays current battery status                    |
| *Speaker “mute” | Power Device Off   |                                         |                                                                                            |


### UX Development - Form Factor / Ergonomics

<p align="center">
  <img src="Assets/Form Factor & Ergonomics.png" alt="Form Factor & Ergonomics" width="80%"/>
</p>


### Manufacturing Recommendations

|                                | Option 1                                                                                       | Option 2A                                                                                     | Option 2B                                                                                     |
|--------------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Case                           | 3D Printed                                                                                     | Injection Molded                                                                               | Injection Molded                                                                               |
| Sleeve                         | Sleeve is Required                                                                             | Sleeve is Optional                                                                             | No Sleeve                                                                                      |
| Cosmetic Impact                | Looks like a finished product but only with a sleeve. 3D printed is sub-par when compared to molded. | Case is highly-cosmetic but sleeve finishes off design                                         | Case is highly-cosmetic                                                                        |
| Size Impact                    | Sleeve adds 1-2 mm in all directions to overall size                                           | Sleeve adds 1-2 mm in all directions to overall size                                           | Smallest Possible Device                                                                       |
| Pocket + Handfeel Impact       | Sleeve feels great in the hand, however, decreases pocketability and gathers dust.             | Sleeve feels great in the hand, however, decreases pocketability and gathers dust.             | Use of molded texture provides great handfeel and easily goes in and out of the pocket, free of dust. |
| Perceived Value                | Sleeve adds quality finish over low-quality case.                                              | Sleeve can be optional, which may add value                                                    | Lack of sleeve doesn’t decrease value due to part finish/quality                               |
| Cost Impact (USA)              | Roughlt $16.67 each         | Roughlt $15.28 each         | Roughlt $8.61 each                                                                                     |
| Cost Impact (Overseas)         | Roughlt $13.52 each         | Roughlt $6.17 each         | Roughlt $2.65 each                                                                                     |
| Perceived Future-Forward       | Most futuristic but also hidden; more story value                                              | Most futuristic but also hidden; more story value                                              | N/A                                                                                            |


### Material Finish / Part Examples (Injection-molded)

<p align="center">
  <img src="Assets/Material FInish & Part Examples.png" alt="Material Finish & Part Examples" width="80%"/>
</p>


## Appendix



### Manufacturing and Build Vendors

#### Enclosure + Cover
| Part            | Manufacturing Method | Vendor             | Location | Lead Time                                                                               | Cost Per Unit | Notes                                                                                             |
| :-------------: | :------------------: | :----------------: | :------: | :-------------------------------------------------------------------------------------: | :-----------: | :-----------------------------------------------------------------------------------------------: |
| Enclosure       | Injection Molding    | Xometry            | USA      | 25 business days for T1 samples Production parts would ship 2-3 weeks after T1 approval | $8.61         | They think they can shorten the lead time but need final part design first.  5,000 unit tool life |
| Enclosure       | Injection Molding    | SunPe              | China    | 18 business days for tooling 6 business days for production                             | $2.65         | 30,000 unit tool life                                                                             |
| Enclosure       | Form4 Print          | Cad9               | USA      | 400 units a week                                                                        | $10.00        | Pricing was a ballpark from James - he said could be under $10                                    |
| Elastomer Cover | Compression Molding  | Advanced Prototype | USA      | 3-4 wks for mold and T0 samples 2-3 wks for production                                  | $6.67         | 10,000 unit tool life                                                                             |
| Elastomer Cover | Compression Molding  | SunPe              | China    | 32 working days + 3 days shipping                                                       | $3.52         | 30,000 unit tool life                                                                             |

#### PCBA + Box Build

| Field                                                                                       | 1   | 2   | 3              | 4                  |
|---------------------------------------------------------------------------------------------|-----|-----|----------------|--------------------|
| Vendor Name                                                                                 | TASC| PCA | Out of the Box | Schippers and Crew |
| HQ Location                                                                                 | Seattle, WA | Bellevue, WA | Renton, WA | Seattle, WA |
| Website                                                                                     | https://tasc-wa.com/ | https://www.pcacorporation.com/ | https://www.obmfg.com/ | http://schippersandcrew.com/ |
| Contact Name                                                                                | Maggi |  | Mike Lopez |  |
| What sort of timelines are typical for a new program with your company? Planning through to first samples, production, etc. What can we expect? | Depends on complexity - simple could be 1-2 weeks for proof of concept. |  | There are a lot of variables in this question. At a high level and with just what’s seen in the attachment, the project of quoting/ordering parts/assembly/testing could all be done in 10-20-Days. If all data and parts (Components, PCB’s & Stencil) are in-house, PCB Assembly timelines are offered at Same-Day through 15-Days or scheduled drops. This is in regard to components applied to a PCB only. Production or starting production drops could be daily through whatever timeline suits your needs. Our facility is wide open for new work. | Timeline for our turkey build, will depend on the availability of the components but we can expedite our production, production lead time ranges from 3 days to 1 week depending on the number of components and complexity of the build. Our normal production lead time for PCBA is 3 weeks. Add -1 to 2 weeks if testing/programming and box build is included. What you can expect from Schippers are our full support to make sure we launch your product successfully. We have an open-door policy for our client and you can come and work with our team during the assembly process. |
| Do you typically handle fixtures for test or programming internally or expect those to be provided? | Hex files are typically provided for programming. We can perform programming and test. Test fixtures/procedures are something we can help design and manufacture. |  | We’d prefer you to provide test fixturing or devices with clear instructions of the test procedures/programming. We don’t offer programming for test but we can offer the labor to perform and certify the conformance. Typically we’d suggest our OEM’s go to an engineering firm for building that data package. | Majority of our customers are having their boards tested here at Schippers especially those boards needed conformal coating. All fixtures for test and programming are provided by customers. If simple functional test, we may have our own equipment we can use, we just need to understand what kind of testing you required. What you mentioned dual use fixtures are what we currently see provided to us. |
| Assuming you’ll do the PCB Assembly, given details on the attachment, what sort of typical timelines do you have if we’re consigning components to you? | How many SMD components? How many TH components? Are there any BGA's? Consignment standard lead time is 4 wks, Turnkey is 6 wks. We can improve on that on an as needed basis. A final BOM would help determine lead time. |  | You mentioned 100 boards for first runs then 2500 for beta. They look pretty small so 100 of the electronics portion can be completed in less than 5-days for sure. 2500 could be completed in 5/10/15-Days. I don’t quite know what that product has inside it but if there’s more than one PCB or if it’s a flex PCB then lets get more details to talk about. | As mentioned previously, lead time for assembly depends on complexity of the build and number of components. Our consignment lead time ranges from 3 days to 1 week and normal lead time is 2-3 weeks. |
| For PCBs, do you have a vendor or vendors you prefer to work with? | No preference if you are supplying. If TASC is providing we have our vendors we use. |  | We absolutely have PCB vendors. We do use multiple options for the quote process and will have pricing back from them in less than 24 hours. We can also pass their info off to you if you’d like to use them directly and consign. | For PCB fab, yes, we do have a vendor that we preferred to work with, we have domestic and overseas vendors depending on application. Their normal lead time ranges from 4-6 weeks and, for expedite depending on how many layers and complexity. |
| For a full program, can you manage electrical component procurement and have the mechanical components consigned? | YES, if CAD or STP files are available we can also source the enclosure components through Xometry or Fathom or your preferred vendor. |  | Absolutely no problem at all. | Yes, we can do EE procurement and accept ME consigned parts. We can also procure ME parts as long vendors are established especially for the custom parts. |
| What sort of receiving or final QA programs do you have in place? | We operate all jobs through the job with QC sign offs at different stages of the assembly. Final QA would be done at the program and test phase from what I am gathering from your description. |  | Our Engineering produced assembly documentation contains inspection points i.e. Visual Inspection, X-Ray, AOI, Solder validation, etc. Both In-Process and Final. Our in-house FAI and the Assembly Documentation are designed specifically to accommodate all customer PO requirements and needs. | For custom parts that we purchased, it is mandatory to do an in-process inspection, to make sure it is up to spec. For consigned EE/ME parts, it goes thru our kit audit department. Any discrepancy on the counts, mismatch on PN against your BOM will be addressed during kit audit. |

### Documentation
 [Espressif FCC ID Change Authorization Letter](<Assets/Espressif FCC ID Change Authorization Letter_Signed.pdf>)



## Facture
Let’s materialize the future, together.

Contact us:
- Phone: +1 (206) 420 8086
- Email: [info@facture.design](mailto:info@facture.design)
- Website: [www.facture.design](http://www.facture.design)

>**Q2 2024** **FACTURE** Seattle, WA 98134  