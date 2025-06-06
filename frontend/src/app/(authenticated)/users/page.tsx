"use client"

import { useState } from "react"
import { 
  Plus, 
  Search, 
  Users, 
  Settings, 
  MoreHorizontal,
  Edit,
  Trash2,
  UserCheck,
  UserX,
  Eye,
  Mail,
  Phone,
  Shield,
  Crown,
  User
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

// Mock data for users
const users = [
  {
    id: "1",
    name: "Sarah Johnson",
    email: "sarah.johnson@techcorp.com",
    role: "Admin",
    organization: "TechCorp Solutions",
    status: "active",
    lastLogin: "2 hours ago",
    joinDate: "2023-08-15",
    rfpsManaged: 24,
    avatar: "/api/placeholder/32/32"
  },
  {
    id: "2", 
    name: "Michael Chen",
    email: "michael.chen@globalmanuf.com",
    role: "Manager",
    organization: "Global Manufacturing Inc",
    status: "active",
    lastLogin: "1 day ago",
    joinDate: "2023-09-22",
    rfpsManaged: 18,
    avatar: "/api/placeholder/32/32"
  },
  {
    id: "3",
    name: "Emily Rodriguez", 
    email: "emily.rodriguez@hsa.org",
    role: "User",
    organization: "Healthcare Systems Alliance",
    status: "active",
    lastLogin: "3 hours ago",
    joinDate: "2023-10-05",
    rfpsManaged: 12,
    avatar: "/api/placeholder/32/32"
  },
  {
    id: "4",
    name: "David Kim",
    email: "david.kim@scg.com",
    role: "User",
    organization: "Strategic Consulting Group", 
    status: "inactive",
    lastLogin: "2 weeks ago",
    joinDate: "2023-07-18",
    rfpsManaged: 8,
    avatar: "/api/placeholder/32/32"
  },
  {
    id: "5",
    name: "Lisa Thompson",
    email: "lisa.thompson@techcorp.com",
    role: "Manager",
    organization: "TechCorp Solutions",
    status: "active",
    lastLogin: "30 minutes ago", 
    joinDate: "2023-11-12",
    rfpsManaged: 15,
    avatar: "/api/placeholder/32/32"
  }
]

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedRole, setSelectedRole] = useState("all")
  const [selectedStatus, setSelectedStatus] = useState("all")

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.organization.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = selectedRole === "all" || user.role.toLowerCase() === selectedRole
    const matchesStatus = selectedStatus === "all" || user.status === selectedStatus
    return matchesSearch && matchesRole && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    const variants = {
      active: { color: "bg-green-100 text-green-800", text: "Active" },
      inactive: { color: "bg-gray-100 text-gray-800", text: "Inactive" },
      pending: { color: "bg-yellow-100 text-yellow-800", text: "Pending" }
    }
    
    const config = variants[status as keyof typeof variants] || variants.active
    return <Badge className={config.color}>{config.text}</Badge>
  }

  const getRoleBadge = (role: string) => {
    const variants = {
      admin: { color: "bg-red-100 text-red-800", icon: Crown, text: "Admin" },
      manager: { color: "bg-blue-100 text-blue-800", icon: Shield, text: "Manager" },
      user: { color: "bg-purple-100 text-purple-800", icon: User, text: "User" }
    }
    
    const config = variants[role.toLowerCase() as keyof typeof variants] || variants.user
    const Icon = config.icon
    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {config.text}
      </Badge>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            User Management
          </h1>
          <p className="text-muted-foreground text-lg">
            Manage user accounts, roles, and permissions
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" />
          Invite User
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Users</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <Users className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{users.length}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              {users.filter(u => u.status === 'active').length} active users
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Active Sessions</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <UserCheck className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              {users.filter(u => u.status === 'active').length}
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Currently online
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Admins</CardTitle>
            <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
              <Crown className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {users.filter(u => u.role === 'Admin').length}
            </div>
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
              System administrators
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Avg RFPs</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <Settings className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
              {Math.round(users.reduce((sum, u) => sum + u.rfpsManaged, 0) / users.length)}
            </div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              RFPs per user
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Shield className="mr-2 h-4 w-4" />
              Role: {selectedRole === 'all' ? 'All' : selectedRole}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setSelectedRole("all")}>
              All Roles
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedRole("admin")}>
              Admin
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedRole("manager")}>
              Manager
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedRole("user")}>
              User
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <UserCheck className="mr-2 h-4 w-4" />
              Status: {selectedStatus === 'all' ? 'All' : selectedStatus}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setSelectedStatus("all")}>
              All Status
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("active")}>
              Active
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("inactive")}>
              Inactive
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("pending")}>
              Pending
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Users Table */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            User Directory
          </CardTitle>
          <CardDescription>
            Complete list of all platform users and their details
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Organization</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>RFPs Managed</TableHead>
                <TableHead>Last Login</TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <Avatar>
                        <AvatarImage src={user.avatar} alt={user.name} />
                        <AvatarFallback className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-muted-foreground">{user.email}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{user.organization}</div>
                  </TableCell>
                  <TableCell>
                    {getRoleBadge(user.role)}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(user.status)}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{user.rfpsManaged}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{user.lastLogin}</div>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>
                          <Eye className="mr-2 h-4 w-4" />
                          View Profile
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit User
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Mail className="mr-2 h-4 w-4" />
                          Send Message
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        {user.status === 'active' ? (
                          <DropdownMenuItem>
                            <UserX className="mr-2 h-4 w-4" />
                            Deactivate
                          </DropdownMenuItem>
                        ) : (
                          <DropdownMenuItem>
                            <UserCheck className="mr-2 h-4 w-4" />
                            Activate
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem className="text-destructive">
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete User
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}