import React, { useState } from 'react';
import { Modal, Upload, Button, message, Alert, Typography, Space } from 'antd';
import { UploadOutlined, FileExcelOutlined, FileTextOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import type { RcFile } from 'antd/es/upload';
import api from '../api/api';
import { getApiBaseUrl } from '../utils/config';

const { Text, Link, Paragraph } = Typography;

interface ImportModalProps {
  visible: boolean;
  title: string;
  endpoint: string;
  templateUrl?: string;
  onClose: () => void;
  onSuccess: () => void;
  acceptedFileTypes?: string;
  helpText?: React.ReactNode;
}

const ImportModal: React.FC<ImportModalProps> = ({
  visible,
  title,
  endpoint,
  templateUrl,
  onClose,
  onSuccess,
  acceptedFileTypes = '.csv,.xlsx,.xls',
  helpText
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    const formData = new FormData();

    if (fileList.length === 0) {
      message.error('请先选择文件');
      return;
    }

    const file = fileList[0] as RcFile;
    formData.append('file', file);

    setUploading(true);
    setError(null);

    try {
      // 获取token
      const token = localStorage.getItem('token');

      // 使用fetch API直接发送请求
      const apiBaseUrl = getApiBaseUrl();
      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`导入失败: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      console.log('导入成功:', data);

      setFileList([]);
      message.success('导入成功');
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('导入失败:', error);

      setError(error.message || '导入失败，请稍后重试');
    } finally {
      setUploading(false);
    }
  };

  const uploadProps: UploadProps = {
    onRemove: () => {
      setFileList([]);
    },
    beforeUpload: (file) => {
      // 检查文件类型
      const isAcceptedType = acceptedFileTypes
        .split(',')
        .some(type => file.name.toLowerCase().endsWith(type.replace('.', '')));

      if (!isAcceptedType) {
        message.error(`只支持${acceptedFileTypes}格式的文件`);
        return Upload.LIST_IGNORE;
      }

      // 检查文件大小，限制为10MB
      const isLessThan10M = file.size / 1024 / 1024 < 10;
      if (!isLessThan10M) {
        message.error('文件大小不能超过10MB');
        return Upload.LIST_IGNORE;
      }

      setFileList([file]);
      return false;
    },
    fileList,
  };

  const getFileTypeIcon = () => {
    if (acceptedFileTypes.includes('csv')) {
      return <FileTextOutlined />;
    }
    if (acceptedFileTypes.includes('xls') || acceptedFileTypes.includes('xlsx')) {
      return <FileExcelOutlined />;
    }
    return <UploadOutlined />;
  };

  return (
    <Modal
      title={title}
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="back" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={uploading}
          onClick={handleUpload}
          disabled={fileList.length === 0}
        >
          导入
        </Button>,
      ]}
    >
      {error && (
        <Alert
          message="导入错误"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Paragraph>
        请选择要导入的文件，支持{acceptedFileTypes}格式。
      </Paragraph>

      {helpText && (
        <Alert
          message="导入说明"
          description={helpText}
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Upload {...uploadProps}>
        <Button icon={getFileTypeIcon()}>选择文件</Button>
      </Upload>

      {templateUrl && (
        <div style={{ marginTop: 16 }}>
          <Space>
            <QuestionCircleOutlined />
            <Text>不知道如何准备数据？</Text>
            <Link href={templateUrl} target="_blank">下载模板</Link>
          </Space>
        </div>
      )}
    </Modal>
  );
};

export default ImportModal;
