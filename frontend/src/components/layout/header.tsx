"use client"

import { useState } from "react"
import { Bell, Search, Moon, Sun, User, LogOut, Settings } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "next/navigation"

export function Header() {
  const [searchQuery, setSearchQuery] = useState("")
  const { setTheme, theme } = useTheme()
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  const userInitials = user?.full_name
    ?.split(" ")
    .map(name => name[0])
    .join("")
    .toUpperCase() || "U"

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search RFPs, templates, or documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 h-10 w-full bg-gray-50 dark:bg-gray-800 border-0 rounded-xl shadow-sm focus:shadow-md transition-shadow"
            />
          </div>
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative h-10 w-10 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800">
                <Bell className="h-5 w-5" />
                <Badge 
                  variant="destructive" 
                  className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
                >
                  3
                </Badge>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-96">
              <DropdownMenuLabel className="flex items-center justify-between p-4 border-b">
                <span className="font-semibold">Notifications</span>
                <Badge variant="secondary" className="text-xs">3 new</Badge>
              </DropdownMenuLabel>
              <div className="max-h-80 overflow-y-auto">
                <div className="p-2 space-y-1">
                  <div className="rounded-lg p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-blue-900 dark:text-blue-100">New RFP Received</p>
                        <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                          IT Infrastructure Upgrade - Due in 5 days
                        </p>
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-2">2 minutes ago</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="rounded-lg p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-green-900 dark:text-green-100">Proposal Approved</p>
                        <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                          Software Development Project - $50k
                        </p>
                        <p className="text-xs text-green-600 dark:text-green-400 mt-2">1 hour ago</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="rounded-lg p-4 bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800 hover:bg-purple-100 dark:hover:bg-purple-900 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-purple-900 dark:text-purple-100">AI Analysis Complete</p>
                        <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">
                          Marketing Campaign RFP analysis ready
                        </p>
                        <p className="text-xs text-purple-600 dark:text-purple-400 mt-2">3 hours ago</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="border-t p-2">
                <Button variant="ghost" className="w-full text-sm">
                  View all notifications
                </Button>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="h-10 w-10 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 p-0">
                <Avatar className="h-10 w-10">
                  <AvatarImage src="" alt={user?.full_name || ""} />
                  <AvatarFallback className="text-sm bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user?.full_name}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user?.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push("/profile")}>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push("/settings")}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}