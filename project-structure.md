# โครงสร้างโปรเจค gRPC Image Service POC

## ภาพรวม
โปรเจคนี้เป็น POC (Proof of Concept) สำหรับระบบประมวลผลภาพด้วย gRPC ที่ใช้ Redis และ RabbitMQ เป็น message queue

## โครงสร้างไดเรกทอรี

```
src/
├── client/                     # Client applications
│   ├── api-consumer/          # RabbitMQ consumer → gRPC client
│   └── api-producer/          # HTTP API → Redis/RabbitMQ publisher
├── server/
│   ├── sample_service/        # gRPC server (port 50052)
│   └── docker-compose.yml     # Services orchestration
├── protos/
│   └── sample_service.proto   # Protocol Buffers definition
└── tools/
    ├── protogen.json          # Protobuf generation config
    └── simple_gen.sh          # Code generation script
```

## คอมโพเนนต์หลัก

### 1. gRPC Server (`src/server/sample_service/`)
- รันบนพอร์ต 50052
- ให้บริการ: ProcessSample, GetSampleStatus, Health
- ใช้ Protocol Buffers สำหรับ API definition

### 2. API Producer (`src/client/api-producer/`)
- HTTP API server บนพอร์ต 8000
- รับ HTTP requests และส่งไปยัง Redis/RabbitMQ
- ใช้สำหรับรับ tasks จาก external clients

### 3. API Consumer (`src/client/api-consumer/`)
- Subscribe จาก RabbitMQ queue
- เรียก gRPC server เพื่อประมวลผล
- ทำหน้าที่เป็นตัวกลางระหว่าง queue และ gRPC

### 4. Protocol Definition (`src/protos/sample_service.proto`)
- กำหนด gRPC services และ message types
- รองรับการประมวลผลภาพและตรวจสอบสถานะ

## การรันระบบ

```bash
# เริ่มทุก services พร้อมกัน
make dev-services

# หรือรันแยกจากคอมมานด์ใน README.MD
```

## Message Flow
HTTP Request → API Producer → Redis/RabbitMQ → API Consumer → gRPC Server