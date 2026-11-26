//go:build !windows

package main

import "log"

func openBrowser(url string) error { log.Println("OPEN", url); return nil }
func showMessage(s string)         { log.Println(s) }
