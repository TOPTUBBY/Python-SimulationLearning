//go:build windows

package main

import (
	"fmt"
	"syscall"
	"unsafe"
)

func winString(s string) *uint16 { p, _ := syscall.UTF16PtrFromString(s); return p }
func openBrowser(url string) error {
	shell := syscall.NewLazyDLL("shell32.dll").NewProc("ShellExecuteW")
	rc, _, _ := shell.Call(0, uintptr(unsafe.Pointer(winString("open"))), uintptr(unsafe.Pointer(winString(url))), 0, 0, 1)
	if rc <= 32 {
		return fmt.Errorf("ShellExecute failed (%d)", rc)
	}
	return nil
}
func showMessage(s string) {
	dialog := syscall.NewLazyDLL("user32.dll").NewProc("MessageBoxW")
	dialog.Call(0, uintptr(unsafe.Pointer(winString(s))), uintptr(unsafe.Pointer(winString("SimulationLearning | How It's Wired | 8131"))), 0x40|0x1000)
}
