"use client"

import { useState } from "react"
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Globe,
  Save,
  Eye,
  EyeOff
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function SettingsPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [profileData, setProfileData] = useState({
    fullName: "John Doe",
    email: "rfp@kzahhar.com",
    phone: "+1 (555) 123-4567",
    organization: "TechCorp Solutions",
    role: "Admin",
    timezone: "America/New_York",
    language: "en",
    currency: "SAR"
  })

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    rfpDeadlines: true,
    proposalUpdates: true,
    teamUpdates: false,
    marketingEmails: false
  })

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    loginAlerts: true,
    sessionTimeout: "30",
    passwordExpiry: "90"
  })

  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: "light",
    language: "en",
    dateFormat: "MM/DD/YYYY",
    timeFormat: "12h"
  })

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Settings
          </h1>
          <p className="text-muted-foreground text-lg">
            Manage your account preferences and system configuration
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Save className="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Settings */}
        <Card className="lg:col-span-2 border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Profile Information
            </CardTitle>
            <CardDescription>
              Update your personal information and account details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 p-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  value={profileData.fullName}
                  onChange={(e) => setProfileData({...profileData, fullName: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={profileData.phone}
                  onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="organization">Organization</Label>
                <Input
                  id="organization"
                  value={profileData.organization}
                  onChange={(e) => setProfileData({...profileData, organization: e.target.value})}
                />
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="timezone">Timezone</Label>
                <Select value={profileData.timezone} onValueChange={(value) => setProfileData({...profileData, timezone: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="America/New_York">Eastern Time (ET)</SelectItem>
                    <SelectItem value="America/Chicago">Central Time (CT)</SelectItem>
                    <SelectItem value="America/Denver">Mountain Time (MT)</SelectItem>
                    <SelectItem value="America/Los_Angeles">Pacific Time (PT)</SelectItem>
                    <SelectItem value="Asia/Riyadh">Arabia Standard Time</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="language">Language</Label>
                <Select value={profileData.language} onValueChange={(value) => setProfileData({...profileData, language: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="ar">العربية</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <Select value={profileData.currency} onValueChange={(value) => setProfileData({...profileData, currency: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SAR">Saudi Riyal (SAR)</SelectItem>
                    <SelectItem value="USD">US Dollar (USD)</SelectItem>
                    <SelectItem value="EUR">Euro (EUR)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Summary */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Account Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Account Type</span>
                <Badge className="bg-blue-100 text-blue-800">Enterprise Admin</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Subscription</span>
                <Badge className="bg-green-100 text-green-800">Active</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Last Login</span>
                <span className="text-sm text-muted-foreground">2 hours ago</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Member Since</span>
                <span className="text-sm text-muted-foreground">Jan 2024</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-950 dark:to-yellow-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
            </CardTitle>
            <CardDescription>
              Configure how you receive notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            {Object.entries(notificationSettings).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <Label htmlFor={key} className="text-sm">
                  {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                </Label>
                <Switch
                  id={key}
                  checked={value}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({...notificationSettings, [key]: checked})
                  }
                />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-950 dark:to-pink-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Security
            </CardTitle>
            <CardDescription>
              Manage your account security settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="twoFactor" className="text-sm">Two-Factor Authentication</Label>
                <Switch
                  id="twoFactor"
                  checked={securitySettings.twoFactorAuth}
                  onCheckedChange={(checked) => 
                    setSecuritySettings({...securitySettings, twoFactorAuth: checked})
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="loginAlerts" className="text-sm">Login Alerts</Label>
                <Switch
                  id="loginAlerts"
                  checked={securitySettings.loginAlerts}
                  onCheckedChange={(checked) => 
                    setSecuritySettings({...securitySettings, loginAlerts: checked})
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sessionTimeout">Session Timeout (minutes)</Label>
                <Select 
                  value={securitySettings.sessionTimeout} 
                  onValueChange={(value) => setSecuritySettings({...securitySettings, sessionTimeout: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15">15 minutes</SelectItem>
                    <SelectItem value="30">30 minutes</SelectItem>
                    <SelectItem value="60">1 hour</SelectItem>
                    <SelectItem value="120">2 hours</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="pt-4 border-t">
                <Button variant="outline" className="w-full">
                  Change Password
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Appearance Settings */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950 dark:to-indigo-950 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Appearance
            </CardTitle>
            <CardDescription>
              Customize the look and feel of your interface
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme">Theme</Label>
                <Select 
                  value={appearanceSettings.theme} 
                  onValueChange={(value) => setAppearanceSettings({...appearanceSettings, theme: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dateFormat">Date Format</Label>
                <Select 
                  value={appearanceSettings.dateFormat} 
                  onValueChange={(value) => setAppearanceSettings({...appearanceSettings, dateFormat: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                    <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                    <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timeFormat">Time Format</Label>
                <Select 
                  value={appearanceSettings.timeFormat} 
                  onValueChange={(value) => setAppearanceSettings({...appearanceSettings, timeFormat: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="12h">12 Hour</SelectItem>
                    <SelectItem value="24h">24 Hour</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-4">
        <Button variant="outline">
          Reset to Defaults
        </Button>
        <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
          <Save className="mr-2 h-4 w-4" />
          Save All Changes
        </Button>
      </div>
    </div>
  )
}