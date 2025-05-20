import React, { useState, useEffect } from 'react';
import {
  Card, Form, Input, Button, message, Space, Divider, Typography, Switch, Row, Col
} from 'antd';
import { SaveOutlined, UndoOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { getConfig, updateConfig, resetConfig } from '../../utils/config';
import { refreshApiInstance } from '../../api/api';

const { Title, Paragraph, Text } = Typography;

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testingApi, setTestingApi] = useState(false);
  const [apiTestResult, setApiTestResult] = useState<{success: boolean, message: string} | null>(null);

  // 初始化表单
  useEffect(() => {
    const config = getConfig();
    form.setFieldsValue(config);
  }, [form]);

  // 保存配置
  const handleSaveConfig = async (values: ReturnType<typeof getConfig>) => {
    setLoading(true);
    try {
      // 更新配置
      updateConfig(values);

      // 刷新API实例
      refreshApiInstance();

      message.success('配置保存成功');
    } catch (error) {
      console.error('保存配置失败:', error);
      message.error('保存配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 重置配置
  const handleResetConfig = () => {
    const defaultConfig = resetConfig();
    form.setFieldsValue(defaultConfig);

    // 刷新API实例
    refreshApiInstance();

    message.success('配置已重置为默认值');
  };

  // 测试API连接
  const handleTestApiConnection = async () => {
    setTestingApi(true);
    setApiTestResult(null);

    try {
      const apiBaseUrl = form.getFieldValue('apiBaseUrl');
      const response = await fetch(`${apiBaseUrl}/api/health-check`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // 设置较短的超时时间
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        setApiTestResult({
          success: true,
          message: '连接成功！服务器正常响应。'
        });
      } else {
        setApiTestResult({
          success: false,
          message: `连接失败，状态码: ${response.status}`
        });
      }
    } catch (error: any) {
      console.error('API连接测试失败:', error);
      setApiTestResult({
        success: false,
        message: `连接失败: ${error.message || '未知错误'}`
      });
    } finally {
      setTestingApi(false);
    }
  };

  return (
    <Card title="系统设置">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSaveConfig}
        initialValues={getConfig()}
      >
        <Title level={4}>服务器配置</Title>
        <Paragraph>
          设置系统使用的服务器地址，修改后将立即生效。请确保输入正确的地址，否则可能导致系统无法正常工作。
        </Paragraph>

        <Form.Item
          name="apiBaseUrl"
          label="API服务器地址"
          rules={[
            { required: true, message: '请输入API服务器地址' },
            { type: 'url', message: '请输入有效的URL地址' }
          ]}
          extra="API服务器的基础URL，例如: http://xin.work.gd:8000"
        >
          <Input placeholder="请输入API服务器地址" />
        </Form.Item>

        <Space>
          <Button
            type="default"
            onClick={handleTestApiConnection}
            loading={testingApi}
          >
            测试连接
          </Button>

          {apiTestResult && (
            <Text
              type={apiTestResult.success ? 'success' : 'danger'}
              style={{ display: 'flex', alignItems: 'center' }}
            >
              {apiTestResult.success && <CheckCircleOutlined style={{ marginRight: 8 }} />}
              {apiTestResult.message}
            </Text>
          )}
        </Space>

        <Form.Item
          name="templateBaseUrl"
          label="模板文件服务器地址"
          rules={[
            { required: true, message: '请输入模板文件服务器地址' },
            { type: 'url', message: '请输入有效的URL地址' }
          ]}
          extra="模板文件服务器的基础URL，通常与API服务器相同"
        >
          <Input placeholder="请输入模板文件服务器地址" />
        </Form.Item>

        <Divider />

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              保存配置
            </Button>
            <Button
              danger
              icon={<UndoOutlined />}
              onClick={handleResetConfig}
            >
              重置为默认值
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Settings;
