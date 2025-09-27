from mmocr.apis import MMOCRInferencer

def main():
    ocr = MMOCRInferencer(
        det='DBNet',
        det_weights='./models/dbnet_resnet50-oclip_1200e_icdar2015_20221102_115917-bde8c87a.pth',
        rec=None,
    )

if __name__ == "__main__":
    main()